import json
from sqlalchemy.orm import Session
from models import QuizResult, QuestionAnalytics, StudyMaterial

class QuizRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_quiz_result(self, student_id: int, score: int, total: int, quiz_type: str, analytics_data: list[dict], material_id: int = None):
        """Saves quiz result and granular analytics."""
        try:
            result = QuizResult(
                student_id=student_id,
                study_material_id=material_id,
                score=score, 
                total_questions=total, 
                quiz_type=quiz_type
            )
            self.db.add(result)
            self.db.commit()
            self.db.refresh(result)

            for item in analytics_data:
                analytic = QuestionAnalytics(
                    quiz_result_id=result.id,
                    topic=item.get("topic") or "Geral",
                    is_correct=item.get("is_correct")
                )
                self.db.add(analytic)
            
            self.db.commit()
            return True
        except Exception as e:
            print(f"Error saving quiz result: {e}")
            self.db.rollback()
            return False

    def get_student_analytics(self, student_id: int):
        """Calculates success rate per topic for a specific student."""
        try:
            # Get all analytics for this student
            analytics = (
                self.db.query(QuestionAnalytics)
                .join(QuizResult)
                .filter(QuizResult.student_id == student_id)
                .all()
            )
            
            if not analytics: return []

            stats = {} # {topic: {total: 0, correct: 0}}
            
            for a in analytics:
                if a.topic not in stats:
                    stats[a.topic] = {"total": 0, "correct": 0}
                stats[a.topic]["total"] += 1
                if a.is_correct:
                    stats[a.topic]["correct"] += 1
            
            results = []
            for topic, data in stats.items():
                success_rate = (data["correct"] / data["total"]) * 100
                results.append({
                    "topic": topic,
                    "success_rate": round(success_rate),
                    "total_questions": data["total"]
                })
            
            return sorted(results, key=lambda x: x["success_rate"])
            
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

            # Get topics from material (Direct DB access)
            materials = self.db.query(StudyMaterial).filter(StudyMaterial.student_id == student_id).all()
            for m in materials:
                if m.topics:
                    try:
                        t_list = json.loads(m.topics)
                        topics.update(t_list)
                    except:
                        pass
            
            return sorted(list(topics))

        except Exception as e:
            print(f"Error getting all topics: {e}")
            return []
