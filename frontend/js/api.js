// frontend/js/api.js

async function sendMessage(messageText, sessionId) {
    try {
        const payload = {
            message: messageText
        };
        
        if (sessionId) {
            payload.session_id = sessionId;
        }

        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            let errorMsg = "Something went wrong while generating the response.";
            if (response.status === 503) {
                errorMsg = "AI service isn't configured yet.";
            } else if (response.status === 502) {
                errorMsg = "Upstream AI provider error.";
            } else if (response.status === 500) {
                errorMsg = "Unable to connect to the memory system.";
            } else {
                try {
                    const errorData = await response.json();
                    if (errorData.detail) {
                        errorMsg = errorData.detail;
                    }
                } catch (e) {
                    // Ignore JSON parsing errors
                }
            }
            throw new Error(errorMsg);
        }

        const data = await response.json();
        return data;

    } catch (error) {
        console.error("API Error:", error);
        throw error;
    }
}

window.API = {
    sendMessage
};
