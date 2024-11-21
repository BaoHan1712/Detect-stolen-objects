let alertCount = 0;
let ws;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;

function showAlert(message) {
    const alertModal = document.getElementById('alertModal');
    const alertMessage = document.getElementById('alertMessage');
    const alertList = document.getElementById('alertList');
    
    // Hiển thị modal cảnh báo
    alertModal.style.display = 'flex';
    alertMessage.textContent = message;
    
    // Thêm cảnh báo vào danh sách
    const alertTime = new Date().toLocaleTimeString();
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert-item';
    alertDiv.innerHTML = `
        <i class="fas fa-exclamation-circle"></i>
        <span>${message}</span>
        <small>${alertTime}</small>
    `;
    
    alertList.insertBefore(alertDiv, alertList.firstChild);
    alertCount++;
    
    // Giới hạn số lượng cảnh báo hiển thị
    if (alertCount > 5) {
        alertList.removeChild(alertList.lastChild);
        alertCount--;
    }
    
    // Phát âm thanh cảnh báo
    playAlertSound();
}

function closeAlert() {
    document.getElementById('alertModal').style.display = 'none';
}

function playAlertSound() {
    const audio = new Audio('/static/alert.mp3');
    audio.play();
}

// Kết nối với backend qua WebSocket để nhận cảnh báo
function connectWebSocket() {
    ws = new WebSocket(`ws://${window.location.host}/ws`);
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'alert') {
            requestAnimationFrame(() => showAlert(data.message));
        }
    };
    
    ws.onclose = () => {
        if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
            setTimeout(connectWebSocket, 1000);
            reconnectAttempts++;
        }
    };
}

function showNotification(message) {
    const container = document.getElementById('notificationContainer');
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.innerHTML = `
        <i class="fas fa-exclamation-triangle"></i>
        <span>${message}</span>
    `;
    
    container.appendChild(notification);
    
    // Xóa thông báo sau 3 giây
    setTimeout(() => {
        notification.addEventListener('animationend', () => {
            container.removeChild(notification);
        });
    }, 3000);
}

// Cập nhật hàm xử lý WebSocket
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'notification') {
        requestAnimationFrame(() => showNotification(data.message));
    }
};

// Khởi tạo kết nối
document.addEventListener('DOMContentLoaded', function() {
    connectWebSocket();
}); 