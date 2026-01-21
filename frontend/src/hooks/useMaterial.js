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
            const data = await studyService.checkMaterial(studentId);
            if (data.has_material) {
                setSavedMaterial(data);
                setAvailableTopics(data.topics || []);
            } else {
                setSavedMaterial(null);
            }
            // Fetch library list
            const list = await studyService.getMaterials(studentId);
            setMaterialsList(list);
        } catch (err) {
            console.error(err);
        }
    }, [studentId]);

    const handleFileChange = (e) => setFile(e.target.files[0]);

    const analyzeFile = async () => {
        if (!file || !studentId) return;
        setIsAnalyzing(true);
        setErrorMsg('');
        try {
            await studyService.uploadFile(file, studentId);
            await checkSavedMaterial();
            setFile(null); // Clear file selection after upload
        } catch (err) {
            console.error(err);
            setErrorMsg("Falha ao analisar o ficheiro.");
        } finally {
            setIsAnalyzing(false);
        }
    };

    const detectTopics = async () => {
        if (!studentId) return;
        setIsAnalyzing(true);
        setErrorMsg('');
        try {
            const data = await studyService.analyzeTopics(studentId);
            setAvailableTopics(data.topics || []);
            await checkSavedMaterial(); // Refresh to ensure sync
        } catch (err) {
            console.error(err);
            setErrorMsg("Falha ao detetar tópicos.");
        } finally {
            setIsAnalyzing(false);
        }
    };

    const clearMaterial = async () => {
        if (!studentId) return;
        try {
            await studyService.clearMaterial(studentId);
            setSavedMaterial(null);
            setAvailableTopics([]);
        } catch (err) {
            console.error(err);
        }
    };

    const activateMaterial = async (materialId) => {
        if (!studentId) return;
        try {
            await studyService.activateMaterial(studentId, materialId);
            await checkSavedMaterial();
        } catch (err) {
            console.error("Failed to activate material", err);
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
        setErrorMsg,
        refreshMaterial: checkSavedMaterial
    };
};
