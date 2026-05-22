// Асинхронное управление корзиной VKR Habez Factory

function addToCart(productId, quantity) {
    quantity = parseInt(quantity);
    if (isNaN(quantity) || quantity <= 0) {
        showCartToast("Укажите корректное количество товара", "danger");
        return;
    }

    fetch('/catalog/cart/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            product_id: parseInt(productId),
            quantity: quantity
        })
    })
    .then(response => {
        if (response.status === 401) {
            showCartToast("Пожалуйста, войдите в кабинет для заказа", "warning");
            setTimeout(() => {
                window.location.href = "/auth/login";
            }, 1500);
            return null;
        }
        return response.json();
    })
    .then(data => {
        if (!data) return;
        if (data.success) {
            // Обновляем бейдж корзины в навигационной панели
            const badge = document.getElementById('cart-badge');
            if (badge) {
                badge.textContent = data.cart_count;
                badge.classList.remove('d-none');
            }
            showCartToast("Товар добавлен в корзину!", "success");
        } else {
            showCartToast(data.error || "Не удалось добавить товар", "danger");
        }
    })
    .catch(error => {
        console.error('Ошибка добавления в корзину:', error);
        showCartToast("Ошибка сетевого соединения", "danger");
    });
}

function showCartToast(message, type = "success") {
    // Проверяем наличие стилей и элемента тоста
    let toast = document.querySelector('.cart-toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.className = 'cart-toast shadow-sm rounded-1';
        document.body.appendChild(toast);
    }
    
    // Оформление в зависимости от статуса
    let iconClass = "bi-check-circle-fill text-warning";
    if (type === "danger") iconClass = "bi-exclamation-octagon-fill text-danger";
    if (type === "warning") iconClass = "bi-exclamation-triangle-fill text-warning";

    toast.innerHTML = `<i class="bi ${iconClass} fs-5"></i> <span class="fw-medium">${message}</span>`;
    
    // Анимация показа
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}
