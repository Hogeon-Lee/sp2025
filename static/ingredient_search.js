let allData = [];

// 검색
function searchIngredients(query = "") {
  fetch(`/api/ingredients?q=${encodeURIComponent(query)}`)
    .then(res => res.json())
    .then(data => {
      allData = data;
      renderList(data);
    });
}

// 리스트 렌더링
function renderList(data) {
  const list = document.getElementById("resultList");
  list.innerHTML = '';
  const filtered = data.filter(item => item.quantity > 0);
  if (filtered.length === 0) {
    list.innerHTML = '<li style="color:#aaa;text-align:center;">검색 결과가 없습니다</li>';
    return;
  }
  filtered.forEach(item => {
    const li = document.createElement('li');
    li.innerHTML = `
      <div class="info">${item.name} (${item.quantity}) - ${item.expiration_date} · ${item.type_tag}</div>
      <div class="actions">
      <span style="float:right">
        <button onclick="showEditModal(${item.id})">수정</button>
        <button onclick="updateStatus(${item.id}, '소비')">소비</button>
        <button onclick="updateStatus(${item.id}, '버림')">버림</button>
      </div>
`;
    list.appendChild(li);
  });
}

// 소비/버림 처리
function updateStatus(id, action) {
  const item = allData.find(x => x.id === id);
  if (!item) return;

  const input = prompt(`${action}할 수량을 입력하세요`, "1");
  const useAmount = parseInt(input, 10);
  if (isNaN(useAmount) || useAmount <= 0 || useAmount > item.quantity) {
    alert("올바른 수량을 입력해주세요!");
    return;
  }

  const newQuantity = item.quantity - useAmount;
  const status_tag = action === '소비' ? 'consumed' : 'discarded';

  const updateData = {
    name: item.name,
    register_date: item.register_date,
    expiration_date: item.expiration_date,
    quantity: newQuantity,
    type_tag: item.type_tag,
    status_tag: status_tag
  };

  fetch(`/api/ingredients/${id}`, {
    method: "PUT",
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(updateData)
  }).then(() => {
    searchIngredients(document.querySelector('.search-input').value);
  });
}

// 추가/수정 모달
function showAddModal() {
  document.getElementById("modalTitle").innerText = "식자재 추가";
  document.getElementById("modalId").value = "";
  document.getElementById("modalForm").reset();
  document.getElementById("modal").style.display = "block";
}
function showEditModal(id) {
  const item = allData.find(x => x.id === id);
  if (!item) return;
  document.getElementById("modalTitle").innerText = "식자재 수정";
  document.getElementById("modalId").value = id;
  document.getElementById("modalForm").name.value = item.name;
  document.getElementById("modalForm").register_date.value = item.register_date;
  document.getElementById("modalForm").expiration_date.value = item.expiration_date;
  document.getElementById("modalForm").quantity.value = item.quantity;
  document.getElementById("modalForm").type_tag.value = item.type_tag;
  document.getElementById("modal").style.display = "block";
}

// 모달 닫기
function closeModal() {
  document.getElementById("modal").style.display = "none";
  document.getElementById("modalForm").reset();
}

// 저장/수정 처리
function submitModalForm(event) {
  event.preventDefault();
  const form = event.target;
  const id = form.id.value;
  const today = new Date().toISOString().slice(0, 10)
  const body = {
    name: form.name.value,
    register_date: today,
    expiration_date: form.expiration_date.value,
    quantity: parseInt(form.quantity.value),
    type_tag: form.type_tag.value,
    status_tag: ''
  };

  const url = id ? `/api/ingredients/${id}` : '/api/ingredients';
  const method = id ? 'PUT' : 'POST';

  fetch(url, {
    method: method,
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(body)
  })
  .then(res => res.json())
  .then(() => {
    closeModal();
    searchIngredients(document.querySelector('.search-input').value);
  });
}

// 페이지 로딩 시 초기화
window.onload = () => {
  searchIngredients();
};
