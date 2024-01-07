// 获取容器元素
var container = document.getElementById("webgl-container");

// 创建场景、相机和渲染器
var scene = new THREE.Scene();
var camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
var renderer = new THREE.WebGLRenderer();

renderer.setSize(window.innerWidth, window.innerHeight);
container.appendChild(renderer.domElement);

// 创建几何体
var geometry = new THREE.BufferGeometry();
var positions = []; // 在此处加载 PDB 文件的坐标数据
// 请添加代码来加载 PDB 文件并将坐标数据存储在 positions 中

var positionsFloat32Array = new Float32Array(positions);
geometry.addAttribute('position', new THREE.BufferAttribute(positionsFloat32Array, 3));

// 创建材质和网格
var material = new THREE.PointsMaterial({ color: 0x00ff00, size: 0.05 });
var points = new THREE.Points(geometry, material);
scene.add(points);

// 设置相机位置
camera.position.z = 5;

// 创建动画函数
var animate = function () {
    requestAnimationFrame(animate);
    points.rotation.x += 0.01;
    points.rotation.y += 0.01;
    renderer.render(scene, camera);
};

// 启动动画
animate();
