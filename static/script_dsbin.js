// 获取文件输入框元素
const ligandFileInput = document.getElementById('ligand-file');
const proteinFileInput = document.getElementById('protein-file');

// 获取预测按钮元素
const predictButton = document.getElementById('predict-button');

// 获取结果区域元素
const resultArea = document.getElementById('result-area');

// 预测按钮点击事件监听
predictButton.addEventListener('click', () => {
  // 创建FormData对象并添加选定的文件
  const formData = new FormData();
  formData.append('ligand-file', ligandFileInput.files[0]);
  formData.append('protein-file', proteinFileInput.files[0]);

  // 创建XMLHttpRequest对象
  const xhr = new XMLHttpRequest();

  // 设置请求方法和URL
  xhr.open('POST', '/');

  // 设置响应类型
  xhr.responseType = 'json';

  // 发送请求并等待响应
  xhr.send(formData);

  xhr.onload = () => {
    // 更新结果区域的内容
    resultArea.textContent = `Affinity should be: ${xhr.response}`;
  };

  xhr.onerror = () => {
    // 更新结果区域的内容
    resultArea.textContent = 'Something went wrong!';
  };
});
