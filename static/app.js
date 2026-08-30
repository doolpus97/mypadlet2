// Google 이미지 검색 요청
async function searchImages() {
  const query = document.getElementById('imageSearchQuery').value.trim();
  const resultsContainer = document.getElementById('imageSearchResults');
  
  if (!query) {
    alert('검색어를 입력해 주세요.');
    return;
  }
  
  resultsContainer.innerHTML = '<p style="grid-column: 1/-1; text-align: center;">이미지를 검색 중입니다...</p>';

  try {
    const response = await fetch(`/api/search-images?q=${encodeURIComponent(query)}`);
    const data = await response.json();

    resultsContainer.innerHTML = '';

    if (!data.items || data.items.length === 0) {
      resultsContainer.innerHTML = '<p style="grid-column: 1/-1; text-align: center;">검색 결과가 없습니다.</p>';
      return;
    }

    // 검색된 이미지 목록 출력
    data.items.forEach(item => {
      const imgElem = document.createElement('img');
      imgElem.src = item.link;
      imgElem.alt = item.title || '검색 이미지';
      imgElem.style.width = '100%';
      imgElem.style.height = '120px';
      imgElem.style.objectFit = 'cover';
      imgElem.style.cursor = 'pointer';
      imgElem.style.borderRadius = '6px';
      
      // 이미지 클릭 시 게시물 작성 폼으로 전달
      imgElem.onclick = () => selectImage(item.link);
      resultsContainer.appendChild(imgElem);
    });
  } catch (error) {
    console.error('이미지 검색 오류:', error);
    resultsContainer.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: red;">검색 중 오류가 발생했습니다.</p>';
  }
}

// 선택한 이미지 적용
function selectImage(imageUrl) {
  // hidden input에 선택한 이미지 URL 저장
  document.getElementById('postImageUrl').value = imageUrl;
  
  // 미리보기 이미지 업데이트
  const previewImg = document.getElementById('imagePreview');
  const previewContainer = document.getElementById('imagePreviewContainer');
  
  if (previewImg && previewContainer) {
    previewImg.src = imageUrl;
    previewContainer.style.display = 'block';
  }

  closeImageModal();
}

// 모달 열기/닫기
function openImageModal() {
  document.getElementById('imageSearchModal').style.display = 'block';
  document.getElementById('imageSearchQuery').focus();
}

function closeImageModal() {
  document.getElementById('imageSearchModal').style.display = 'none';
  document.getElementById('imageSearchResults').innerHTML = '';
  document.getElementById('imageSearchQuery').value = '';
}