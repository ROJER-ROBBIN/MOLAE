// frontend/js/storage.js

const STORAGE_KEY = 'chitraguptar_session';

function getSessionData() {
    try {
        const data = localStorage.getItem(STORAGE_KEY);
        return data ? JSON.parse(data) : { session_id: null, messages: [] };
    } catch (e) {
        console.error("Failed to read from localStorage", e);
        return { session_id: null, messages: [] };
    }
}

function saveSessionData(data) {
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    } catch (e) {
        console.error("Failed to save to localStorage", e);
    }
}

function getSessionId() {
    return getSessionData().session_id;
}

function setSessionId(sessionId) {
    const data = getSessionData();
    data.session_id = sessionId;
    saveSessionData(data);
}

function getMessages() {
    return getSessionData().messages;
}

function saveMessage(role, content, source = null, memories = null) {
    const data = getSessionData();
    const msg = { role, content, source, memories };
    data.messages.push(msg);
    saveSessionData(data);
}

function clearSession() {
    saveSessionData({ session_id: null, messages: [] });
}

window.Storage = {
    getSessionId,
    setSessionId,
    getMessages,
    saveMessage,
    clearSession
};
