let allData = [];
let editingId = null;

function searchIngredients(keyword = "") {
  fetch(`/api/ingredients?q=${encodeURIComponent(keyword)}`)
    .then(res => res.json())
    .then(data => {
      allData = data;
      renderList(data);
    });
}

function renderList(data) {
  const list = document.getElementById("resultList");
  list.innerHTML = '';
  if (data.length === 0) {
    list.innerHTML = '<li style="color:#aaa;text-align:center;">검색 결과가 없습니다</li>';
    return;
  }
  data.forEach(item => {
    const li = document.createElement('li');
    li.innerHTML = `
      <span>${item.ingredient} (${item.amount}) - ${item.date}</span>
      <span style="float:right">
        <button onclick="showEditModal(${item.id})">수정</button>
        <button onclick="deleteIngredient(${item.id})">삭제</button>
      </span>
    `;
    list.appendChild(li);
  });
}

function showAddModal() {
  editingId = null;
  document.getElementById("modalTitle").innerText = "식자재 추가";
  document.getElementById("modalForm").reset();
  document.getElementById("modalId").value = "";
  document.getElementById("modal").style.display = "flex";
}

function showEditModal(id) {
  const item = allData.find(x => x.id === id);
  if (!item) return;
  editingId = id;
  document.getElementById("modalTitle").innerText = "식자재 수정";
  document.getElementById("modalId").value = item.id;
  document.querySelector("[name=ingredient]").value = item.ingredient;
  document.querySelector("[name=date]").value = item.date;
  document.querySelector("[name=amount]").value = item.amount;
  document.querySelector("[name=type]").value = item.type;
  document.getElementById("modal").style.display = "flex";
}

function closeModal() {
  document.getElementById("modal").style.display = "none";
}

function submitModalForm(e) {
  e.preventDefault();
  const form = e.target;
  const data = {
    ingredient: form.ingredient.value,
    date: form.date.value,
    amount: form.amount.value,
    type: form.type.value
  };
  const id = form.id.value;
  if (id) {
    // 수정
    fetch(`/api/ingredients/${id}`, {
      method: "PUT",
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(data)
    }).then(() => {
      closeModal();
      searchIngredients(document.querySelector('.search-input').value);
    });
  } else {
    // 추가
    fetch("/api/ingredients", {
      method: "POST",
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(data)
    }).then(() => {
      closeModal();
      searchIngredients(document.querySelector('.search-input').value);
    });
  }
}

function deleteIngredient(id) {
  if (!confirm("정말 삭제하시겠습니까?")) return;
  fetch(`/api/ingredients/${id}`, {method: "DELETE"})
    .then(() => searchIngredients(document.querySelector('.search-input').value));
}

// 최초 목록 로딩
window.onload = () => searchIngredients();
