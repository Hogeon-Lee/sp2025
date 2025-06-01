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
  // *** amount가 0인 것은 표시하지 않음 ***
  const filtered = data.filter(item => item.amount > 0);
  if (filtered.length === 0) {
    list.innerHTML = '<li style="color:#aaa;text-align:center;">검색 결과가 없습니다</li>';
    return;
  }
  filtered.forEach(item => {
    const li = document.createElement('li');
    li.innerHTML = `
      <span>
        ${item.ingredient} (${item.amount}) - ${item.date} · ${item.type}
      </span>
      <span style="float:right">
        <button onclick="showEditModal(${item.id})">수정</button>
        <button onclick="updateStatus(${item.id}, '소비')">소비</button>
        <button onclick="updateStatus(${item.id}, '버림')">버림</button>
      </span>
    `;
    list.appendChild(li);
  });
}

// 소비/버림 처리
function updateStatus(id, action) {
  const item = allData.find(x => x.id === id);
  if (!item) return;

  let newAmount = item.amount;
  let consumedAmount = 0;
  let discardedAmount = 0;

  if (action === '소비') {
    const input = prompt("소비할 수량을 입력하세요", "1");
    const useAmount = parseInt(input, 10);

    if (isNaN(useAmount) || useAmount <= 0) {
      alert("올바른 수량을 입력해주세요!");
      return;
    }
    if (useAmount > item.amount) {
      alert("현재 수량보다 많이 소비할 수 없습니다!");
      return;
    }
    newAmount = item.amount - useAmount;
    consumedAmount = useAmount;
  } else if (action === '버림') {
    const input = prompt("버릴 수량을 입력하세요", "1");
    const useAmount = parseInt(input, 10);

    if (isNaN(useAmount) || useAmount <= 0) {
      alert("올바른 수량을 입력해주세요!");
      return;
    }
    if (useAmount > item.amount) {
      alert("현재 수량보다 많이 버릴 수 없습니다!");
      return;
    }
    newAmount = item.amount - useAmount;
    discardedAmount = useAmount;
  }

  const updateData = {
    ingredient: item.ingredient,
    date: item.date,
    amount: newAmount,
    type: item.type,
    consumed_amount: consumedAmount,
    discarded_amount: discardedAmount
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
  document.getElementById("modalForm").ingredient.value = item.ingredient;
  document.getElementById("modalForm").date.value = item.date;
  document.getElementById("modalForm").amount.value = item.amount;
  document.getElementById("modalForm").type.value = item.type;
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
  const body = {
    ingredient: form.ingredient.value,
    date: form.date.value,
    amount: parseInt(form.amount.value),
    type: form.type.value,
    consumed_amount: 0, // 새 추가는 0
    discarded_amount: 0
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
