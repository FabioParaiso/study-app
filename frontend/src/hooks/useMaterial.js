import { useState, useCallback, useEffect } from 'react';
import { studyService } from '../services/studyService';

export const useMaterial = (studentId) => {
    const [file, setFile] = useState(null);
    const [savedMaterial, setSavedMaterial] = useState(null);
    const [availableTopics, setAvailableTopics] = useState([]);
    const [selectedTopic, setSelectedTopic] = useState("all");
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [errorMsg, setErrorMsg] = useState('');

    const [materialsList, setMaterialsList] = useState([]);

    const normalizeTopicList = useCallback((rawTopics) => {
        const list = Array.isArray(rawTopics) ? rawTopics : Object.keys(rawTopics || {});
        return list.sort();
    }, []);

    const syncTopics = useCallback((topicList) => {
        setAvailableTopics(topicList);
        setSelectedTopic(prev => (prev === 'all' || topicList.includes(prev) ? prev : 'all'));
    }, []);

    const checkSavedMaterial = useCallback(async () => {
        if (!studentId) {
            setSavedMaterial(null);
            syncTopics([]);
            setSelectedTopic("all");
            setMaterialsList([]);
            return;
        }
        try {
            const data = await studyService.checkMaterial();
            if (data.has_material) {
                setSavedMaterial(data);

                // Handle new Dictionary structure {Topic: [Concepts]}
                const topicList = normalizeTopicList(data.topics);
                syncTopics(topicList);
            } else {
                setSavedMaterial(null);
                syncTopics([]);
                setSelectedTopic("all");
            }
            // Fetch library list
            const list = await studyService.getMaterials();
            setMaterialsList(list);
        } catch (err) {
            console.error(err);
        }
    }, [studentId, normalizeTopicList, syncTopics]);

    const handleFileChange = (e) => setFile(e.target.files[0]);

    const analyzeFile = async () => {
        if (!file || !studentId) return;
        setIsAnalyzing(true);
        setErrorMsg('');
        try {
            await studyService.uploadFile(file);
            await checkSavedMaterial();
            setFile(null); // Clear file selection after upload
        } catch (err) {
            console.error(err);
            const detail = err?.response?.data?.detail;
            setErrorMsg(detail || "Falha ao analisar o ficheiro.");
        } finally {
            setIsAnalyzing(false);
        }
    };

    const detectTopics = async () => {
        if (!studentId) return;
        setIsAnalyzing(true);
        setErrorMsg('');
        try {
            const data = await studyService.analyzeTopics();

            // Handle new Dictionary structure
            const topicList = normalizeTopicList(data.topics);
            syncTopics(topicList);

            await checkSavedMaterial(); // Refresh to ensure sync
        } catch (err) {
            console.error(err);
            const detail = err?.response?.data?.detail;
            setErrorMsg(detail || "Falha ao detetar tópicos.");
        } finally {
            setIsAnalyzing(false);
        }
    };

    const clearMaterial = async () => {
        if (!studentId) return;
        try {
            await studyService.clearMaterial();
            setSavedMaterial(null);
            syncTopics([]);
            setSelectedTopic("all");
        } catch (err) {
            console.error(err);
        }
    };

    const activateMaterial = async (materialId) => {
        if (!studentId) return;
        try {
            await studyService.activateMaterial(materialId);
            await checkSavedMaterial();
        } catch (err) {
            console.error("Failed to activate material", err);
        }
    };

    const deleteMaterial = async (materialId) => {
        if (!studentId) return;
        try {
            await studyService.deleteMaterial(materialId);
            // If the deleted material was the current one, standard checkSavedMaterial handles clearing
            // If it was another one, we just refresh the list
            await checkSavedMaterial();
        } catch (err) {
            console.error("Failed to delete material", err);
            setErrorMsg("Falha ao apagar material.");
        }
    };

    // Auto-check on mount or studentId change
    useEffect(() => {
        checkSavedMaterial();
    }, [checkSavedMaterial]);

    return {
        file,
        savedMaterial,
        availableTopics,
        selectedTopic,
        isAnalyzing,
        errorMsg,
        materialsList,
        setSelectedTopic,
        handleFileChange,
        analyzeFile,
        detectTopics,
        clearMaterial,
        activateMaterial,
        deleteMaterial,
        setErrorMsg,
        refreshMaterial: checkSavedMaterial
    };
};
