import json
from sqlalchemy.orm import Session
from models import QuizResult, QuestionAnalytics, StudyMaterial

class QuizRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_quiz_result(self, student_id: int, score: int, total: int, quiz_type: str, analytics_data: list[dict], material_id: int = None, xp_earned: int = 0):
        """Saves quiz result and granular analytics, and updates study material stats."""
        try:
            result = QuizResult(
                student_id=student_id,
                study_material_id=material_id,
                score=score, 
                total_questions=total, 
                quiz_type=quiz_type
            )
            self.db.add(result)
            
            # Update StudyMaterial stats
            if material_id:
                material = self.db.query(StudyMaterial).filter(StudyMaterial.id == material_id).first()
                if material:
                    material.total_questions_answered += total
                    material.correct_answers_count += score
                    material.total_xp += xp_earned
                    # Check and update high score (assuming score is absolute, or percentage? 
                    # Usually high score is per quiz run. If score is e.g. 5/5, high score is 5.
                    if score > material.high_score:
                        material.high_score = score
                        
            self.db.commit()
            self.db.refresh(result)
            
            for item in analytics_data:
                concept_name = item.get("topic") or "Geral"
                # Try to link to a concept_id
                if concept_name and material_id:
                     from models import Concept, Topic

                     # 1. Exact Match
                     concept = (self.db.query(Concept)
                                .join(Topic)
                                .filter(Topic.study_material_id == material_id, Concept.name == concept_name)
                                .first())
                     
                     # 2. Case Insensitive Fallback
                     if not concept:
                         from sqlalchemy import func
                         concept = (self.db.query(Concept)
                                    .join(Topic)
                                    .filter(Topic.study_material_id == material_id, func.lower(Concept.name) == concept_name.lower())
                                    .first())

                     if concept:
                         concept_id = concept.id

                analytic = QuestionAnalytics(
                    quiz_result_id=result.id,
                    topic=concept_name, # Stores Concept Name
                    concept_id=concept_id,
                    is_correct=item.get("is_correct")
                )
                self.db.add(analytic)
            
            self.db.commit()
            return True
        except Exception as e:
            print(f"Error saving quiz result: {e}")
            self.db.rollback()
            return False

    def get_student_analytics(self, student_id: int, material_id: int = None):
        """
        Calculates success rate per topic/concept.
        ENSURES all concepts from the material are returned, even if never tested (0%).
        Merges orphan analytics by fuzzy name matching.
        """
        try:
            from models import Concept, Topic, StudyMaterial

            # 1. Build the Skeleton (All Topics & Concepts for this material)
            # If no material_id, we might need to fetch all materials for student, but user use-case is mostly single material analysis.
            # For "Weak Points" panel, we usually pass material_id.
            
            skeleton = {} # { (topic_name, concept_name): {total: 0, correct: 0} }
            
            if material_id:
                topics = self.db.query(Topic).filter(Topic.study_material_id == material_id).all()
                for t in topics:
                    for c in t.concepts:
                        skeleton[(t.name, c.name)] = {"total": 0, "correct": 0}
            else:
                # If no material specified, fetch all for student (less common for this view but safe fallback)
                materials = self.db.query(StudyMaterial.id).filter(StudyMaterial.student_id == student_id).all()
                m_ids = [m.id for m in materials]
                topics = self.db.query(Topic).filter(Topic.study_material_id.in_(m_ids)).all()
                for t in topics:
                    for c in t.concepts:
                        skeleton[(t.name, c.name)] = {"total": 0, "correct": 0}

            # 2. Fetch Analytics (History)
            query = (
                self.db.query(QuestionAnalytics)
                .join(QuizResult)
                .filter(QuizResult.student_id == student_id)
            )
            if material_id:
                query = query.filter(QuizResult.study_material_id == material_id)
            
            analytics = query.all()

            # 3. Merge Stats
            for a in analytics:
                # Determine bucket
                t_name = None
                c_name = None

                # Strategy A: Link by ID (The robust way)
                if a.concept_id:
                    # We need to fetch the Concept -> Topic for this ID
                    # Optimisation: Pre-fetch map or simple query? 
                    # Given skeleton is already keyed by names, we might need an ID lookup map.
                    # Or simpler: Just rely on the names stored in the skeleton?
                    # We don't have IDs in skeleton keys. 
                    # Let's trust the 'topic' field string in QuestionAnalytics first if distinct?
                    # No, data integrity says use a.concept_id.
                    
                    # Let's find names from skeletons? No, keys are (Str, Str).
                    # We need a reverse lookup map or just query DB. N+1 risk?
                    # Let's use the 'concept' relationship on 'a' if loaded?
                    # It's an object.
                    if a.concept:
                        c_name = a.concept.name
                        if a.concept.topic:
                            t_name = a.concept.topic.name
                
                # Strategy B: Fallback by Name (For orphans)
                if not t_name or not c_name:
                    potential_c_name = a.topic # This field stores the Concept Name string
                    if potential_c_name:
                        # Try to find this concept in our skeleton keys
                        # This matches "Orphans" to the visual tree
                        found = False
                        for (sk_t, sk_c) in skeleton.keys():
                            if sk_c.lower() == potential_c_name.lower():
                                t_name = sk_t
                                c_name = sk_c
                                found = True
                                break
                        if not found:
                             # Truly unknown concept (maybe from deleted topic?). 
                             # User hates "Outros", but we can't hide data.
                             # Maybe label as "Outros" but hopefully Strategy B catches most.
                             t_name = "Outros"
                             c_name = potential_c_name

                # Aggregate
                # Only if we successfully identified a bucket
                if t_name and c_name:
                    key = (t_name, c_name)
                    if key not in skeleton:
                        skeleton[key] = {"total": 0, "correct": 0}
                    
                    skeleton[key]["total"] += 1
                    if a.is_correct:
                        skeleton[key]["correct"] += 1

            # 4. Format Output
            final_results = []
            for (t_name, c_name), stats in skeleton.items():
                total = stats["total"]
                correct = stats["correct"]
                # Use 0% if total is 0 (Unseen)
                rate = round((correct / total) * 100) if total > 0 else 0
                
                final_results.append({
                    "topic": t_name,
                    "concept": c_name,
                    "success_rate": rate,
                    "total_questions": total
                })

            return sorted(final_results, key=lambda x: (x["topic"], x["success_rate"]))
        except Exception as e:
            print(f"Error calculating analytics: {e}")
            return []

    def get_all_topics(self, student_id: int) -> list[str]:
        """Returns a list of all unique topics used in analytics and materials for a student."""
        try:
            # Get topics from analytics for this student
            analytics_topics = (
                self.db.query(QuestionAnalytics.topic)
                .join(QuizResult)
                .filter(QuizResult.student_id == student_id)
                .distinct()
                .all()
            )
            topics = {t[0] for t in analytics_topics if t[0]}
            
            # We also need topics from current material to deduplicate?
            # Ideally the MaterialRepository should handle material topics.
            # But the 'Extract Topics' service needs ALL topics (historic + current) to deduplicate.
            # So this method in QuizRepository might need to call MaterialRepository or the Caller should aggregation.
            # For strict ISP, QuizRepo should only return Analytics topics. MaterialRepo returns Material topics.
            # But let's keep it here for simplicity or split it in the Service layer.
            
            # Let's check implementing just analytics topics here, and assume the caller merges.
            # Wait, the original `get_all_topics` merged both.
            # To follow SRP, QuizRepository should only know about Quiz topics.
            # MaterialRepository should know about Material topics.
            # The Service calling this should merge them.
            
            # However, I cannot easily inject MaterialRepo into QuizRepo.
            # So I will query StudyMaterial here JUST for the topics column, strictly speaking it's a cross-concern but acceptable for query speed OR
            # Better: separate getting material topics to MaterialRepo and merge in TopicService.
            
            # For now to minimize change impact, I will query StudyMaterial table directly here as it was before,
            # but acknowledging it's a slight coupling.
            
            # Get topics from analytics
            analytics_topics = (
                self.db.query(QuestionAnalytics.topic)
                .join(QuizResult)
                .filter(QuizResult.student_id == student_id)
                .distinct()
                .all()
            )
            topics = {t[0] for t in analytics_topics if t[0]}

            # Get topics from material (Via relations)
            materials = self.db.query(StudyMaterial).filter(StudyMaterial.student_id == student_id).all()
            for m in materials:
                if m.topics: # m.topics is a list of Topic objects
                    for t in m.topics:
                        topics.add(t.name)
            
            return sorted(list(topics))

        except Exception as e:
            print(f"Error getting all topics: {e}")
            return []
