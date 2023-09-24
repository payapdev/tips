document.addEventListener('DOMContentLoaded', () => {
    // CSV 데이터를 JSON으로 변환하는 함수
    function csvJSON(csv) {
        const lines = csv.split('\n');
        const result = [];
        const headers = lines[0].split(',');

        for (let i = 1; i < lines.length; i++) {
            const obj = {};
            const currentLine = lines[i].split(',');

            for (let j = 0; j < headers.length; j++) {
                obj[headers[j]] = currentLine[j];
            }

            result.push(obj);
        }

        return JSON.stringify(result);
    }

    // CSV 파일 불러와서 처리
    fetch('data/test_data.csv')
        .then(response => response.text())
        .then(csvData => {
            // CSV 데이터를 JSON으로 변환
            const jsonData = JSON.parse(csvJSON(csvData));

            // JSON 데이터를 화면에 표시
            const productList = document.getElementById('productList');
            jsonData.forEach(product => {
                const productItem = document.createElement('div');
                productItem.classList.add('product-item');

                const productImage = document.createElement('img');
                productImage.classList.add('product-image');
                productImage.src = `images/tips_data/${product.image_name}`;
                console.log(productImage.src);
                productImage.alt = product.title;
                productItem.appendChild(productImage);

                const productTitle = document.createElement('div');
                productTitle.classList.add('product-name');
                productTitle.textContent = product.title;

                const productPrice = document.createElement('div');
                productPrice.classList.add('product-price');
                productPrice.textContent = `đ${product.min} - đ${product.max}`;

                productItem.appendChild(productImage);
                productItem.appendChild(productTitle);
                productItem.appendChild(productPrice);

                productList.appendChild(productItem);

                productItem.addEventListener('click', () => {
                    window.location.href = `product_detail.html?title=${product.title}&min=${product.min}&max=${product.max}&image=${product.image_name}`;
                });
                
            });
        })
        .catch(error => {
            console.error('데이터를 가져오는 중 오류가 발생했습니다.', error);
        });

    // 로고 클릭 시 제품 목록 페이지로 돌아가기
    const logo = document.querySelector('.logo img');
    logo.addEventListener('click', () => {
        window.location.href = 'index.html';
    });
});
