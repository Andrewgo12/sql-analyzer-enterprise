// static/js/websocket-manager.js

const WS_URL = "ws://localhost:8000/ws/analyze/";
let socket = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 10;
const RECONNECT_INTERVAL = 3000;

/**
 * Establishes a robust WebSocket connection.
 * @param {Function} [onOpen] - Callback for open event.
 * @param {Function} [onMessage] - Callback for message event.
 * @param {Function} [onError] - Callback for error event.
 * @param {Function} [onClose] - Callback for close event.
 */
function connectWebSocket({ onOpen, onMessage, onError, onClose } = {}) {
    if (socket && socket.readyState !== WebSocket.CLOSED) {
        socket.close();
    }

    try {
        socket = new WebSocket(WS_URL);
    } catch (err) {
        console.error("WebSocket creation failed:", err);
        scheduleReconnect();
        return;
    }

    socket.addEventListener("open", () => {
        reconnectAttempts = 0;
        console.log("WebSocket conectado.");
        if (typeof onOpen === "function") onOpen();
        dispatchCustomEvent("ws-open");
    });

    socket.addEventListener("message", (event) => {
        try {
            const data = JSON.parse(event.data);
            handleServerMessage(data);
            if (typeof onMessage === "function") onMessage(data);
            dispatchCustomEvent("ws-message", data);
        } catch (e) {
            console.error("Error parsing message:", e);
            if (typeof onError === "function") onError(e);
        }
    });

    socket.addEventListener("close", (event) => {
        console.warn("WebSocket desconectado. Reintentando...", event);
        if (typeof onClose === "function") onClose(event);
        dispatchCustomEvent("ws-close", event);
        scheduleReconnect();
    });

    socket.addEventListener("error", (error) => {
        console.error("WebSocket error:", error);
        if (typeof onError === "function") onError(error);
        dispatchCustomEvent("ws-error", error);
        socket.close();
    });
}

/**
 * Schedules a reconnect attempt with exponential backoff.
 */
function scheduleReconnect() {
    if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
        reconnectAttempts++;
        setTimeout(() => connectWebSocket(), RECONNECT_INTERVAL * reconnectAttempts);
    } else {
        console.error("Max reconnect attempts reached. WebSocket not connected.");
    }
}

/**
 * Sends a message through the WebSocket if connected.
 * @param {Object} message - The message to send.
 * @returns {boolean} - True if sent, false otherwise.
 */
function sendMessage(message) {
    if (!message || typeof message !== "object") {
        console.warn("Mensaje inválido:", message);
        return false;
    }
    if (socket && socket.readyState === WebSocket.OPEN) {
        try {
            socket.send(JSON.stringify(message));
            return true;
        } catch (err) {
            console.error("Error enviando mensaje:", err);
            return false;
        }
    } else {
        console.warn("WebSocket no está conectado.");
        return false;
    }
}

/**
 * Handles incoming messages from the server and updates the UI.
 * @param {Object} data - The data received from the server.
 */
function handleServerMessage(data) {
    const resultDiv = document.getElementById("analyze-result");
    if (resultDiv) {
        resultDiv.textContent = JSON.stringify(data, null, 2);
    } else {
        console.warn("Elemento 'analyze-result' no encontrado.");
    }
}

/**
 * Dispatches a custom event on the window.
 * @param {string} name - Event name.
 * @param {any} detail - Event detail.
 */
function dispatchCustomEvent(name, detail) {
    window.dispatchEvent(new CustomEvent(name, { detail }));
}

/**
 * Closes the WebSocket connection gracefully.
 */
function closeWebSocket() {
    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.close(1000, "Client closed connection.");
    }
}

// Auto-connect WebSocket when the page loads
window.addEventListener("DOMContentLoaded", () => connectWebSocket());

// Export functions for module use
// export { connectWebSocket, sendMessage, closeWebSocket };