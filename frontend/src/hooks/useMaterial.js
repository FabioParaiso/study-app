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

    const checkSavedMaterial = useCallback(async () => {
        if (!studentId) {
            setSavedMaterial(null);
            setAvailableTopics([]);
            setMaterialsList([]);
            return;
        }
        try {
            const data = await studyService.checkMaterial();
            if (data.has_material) {
                setSavedMaterial(data);

                // Handle new Dictionary structure {Topic: [Concepts]}
                const rawTopics = data.topics || [];
                const topicList = Array.isArray(rawTopics) ? rawTopics : Object.keys(rawTopics).sort();
                setAvailableTopics(topicList);
            } else {
                setSavedMaterial(null);
            }
            // Fetch library list
            const list = await studyService.getMaterials();
            setMaterialsList(list);
        } catch (err) {
            console.error(err);
        }
    }, [studentId]);

    const handleFileChange = (e) => setFile(e.target.files[0]);

    const analyzeFile = useCallback(async () => {
        if (!file || !studentId) return;
        setIsAnalyzing(true);
        setErrorMsg('');
        try {
            await studyService.uploadFile(file);
            await checkSavedMaterial();
            setFile(null); // Clear file selection after upload
        } catch (err) {
            console.error(err);
            setErrorMsg("Falha ao analisar o ficheiro.");
        } finally {
            setIsAnalyzing(false);
        }
    }, [file, studentId, checkSavedMaterial]);

    const detectTopics = useCallback(async () => {
        if (!studentId) return;
        setIsAnalyzing(true);
        setErrorMsg('');
        try {
            const data = await studyService.analyzeTopics();

            // Handle new Dictionary structure
            const rawTopics = data.topics || [];
            const topicList = Array.isArray(rawTopics) ? rawTopics : Object.keys(rawTopics).sort();
            setAvailableTopics(topicList);

            await checkSavedMaterial(); // Refresh to ensure sync
        } catch (err) {
            console.error(err);
            setErrorMsg("Falha ao detetar tópicos.");
        } finally {
            setIsAnalyzing(false);
        }
    }, [studentId, checkSavedMaterial]);

    const clearMaterial = useCallback(async () => {
        if (!studentId) return;
        try {
            await studyService.clearMaterial();
            setSavedMaterial(null);
            setAvailableTopics([]);
        } catch (err) {
            console.error(err);
        }
    }, [studentId]);

    const activateMaterial = useCallback(async (materialId) => {
        if (!studentId) return;
        try {
            await studyService.activateMaterial(materialId);
            await checkSavedMaterial();
        } catch (err) {
            console.error("Failed to activate material", err);
        }
    }, [studentId, checkSavedMaterial]);

    const deleteMaterial = useCallback(async (materialId) => {
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
    }, [studentId, checkSavedMaterial]);

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
