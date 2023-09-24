document.addEventListener('DOMContentLoaded', () => {
    const productImage = document.getElementById('productImage');
    const productName = document.querySelector('.product-detail-name');
    const productPrice = document.querySelector('.product-detail-price');
    const buyButton = document.getElementById('buyButton');

    // URL에서 쿼리 매개변수를 가져오는 함수
    function getQueryParam(param) {
        const urlSearchParams = new URLSearchParams(window.location.search);
        return urlSearchParams.get(param);
    }

    // URL에서 전달된 상품 정보 가져오기
    const title = getQueryParam('title');
    const min = getQueryParam('min');
    const max = getQueryParam('max');
    const image = getQueryParam('image');
    console.log("title: ", title);
    console.log("price: ", min, "-", max);
    console.log("image: ", image);

    // 상품 정보를 페이지에 표시
    productName.textContent = title;
    productPrice.textContent = `Min: ${min}, Max: ${max}`;
    productImage.src = `images/tips_data/${image}`;
    console.log(productImage.src);

    // "Buy Now" 버튼 클릭 시 더 자세한 상품 정보 페이지로 이동
    buyButton.addEventListener('click', () => {
        // 원하는 링크 주소로 이동 (상세 정보 페이지에서는 상품을 구매하는 링크로 이동할 수 있음)
        window.location.href = 'https://example.com/product_purchase';
    });

    // 로고 클릭 시 제품 목록 페이지로 돌아가기
    const logo = document.querySelector('.logo img');
    logo.addEventListener('click', () => {
        window.location.href = 'index.html';
    });
});
