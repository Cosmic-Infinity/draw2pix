const overlay = document.getElementById('image-overlay');
const overlayImg = document.getElementById('overlay-img');
const closeOverlay = document.getElementById('close-overlay');
const canvas = document.getElementById('draw-canvas');
const ctx = canvas.getContext('2d');
const penBtn = document.getElementById('pen-btn');
const eraserBtn = document.getElementById('eraser-btn');
const undoBtn = document.getElementById('undo-btn');
const redoBtn = document.getElementById('redo-btn');
const resetBtn = document.getElementById('reset-btn');
const sizeSlider = document.getElementById('pen-size');
const generateBtn = document.getElementById('generate-btn');
const downloadBtn = document.getElementById('download-btn');

let drawing = false;
let penColor = '#000000';
let penSize = parseInt(sizeSlider.value);
let history = [];
let redoStack = [];

function getCanvasPos(e) {
  const rect = canvas.getBoundingClientRect();
  const scaleX = canvas.width / rect.width;
  const scaleY = canvas.height / rect.height;
  let clientX, clientY;
  if (e.touches) {
    clientX = e.touches[0].clientX;
    clientY = e.touches[0].clientY;
  } else {
    clientX = e.clientX;
    clientY = e.clientY;
  }
  return { x: (clientX - rect.left) * scaleX, y: (clientY - rect.top) * scaleY };
}

function startDrawing(e) {
  e.preventDefault();
  drawing = true;
  const pos = getCanvasPos(e);
  ctx.beginPath();
  ctx.moveTo(pos.x, pos.y);
}

function draw(e) {
  if (!drawing) return;
  e.preventDefault();
  const pos = getCanvasPos(e);
  ctx.lineTo(pos.x, pos.y);
  ctx.strokeStyle = penColor;
  ctx.lineWidth = penSize;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  ctx.stroke();
}

function stopDrawing() {
  if (drawing) {
    drawing = false;
    ctx.closePath();
    saveState();
  }
}

function saveState() {
  redoStack = [];
  history.push(canvas.toDataURL());
  if (history.length > 50) history.shift();
}

function restoreState(url) {
  const img = new Image();
  img.src = url;
  img.onload = () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
  };
}

penBtn.addEventListener('click', () => {
  penColor = '#000000';
  penBtn.style.background = '#8D6BFF';
  eraserBtn.style.background = 'linear-gradient(135deg, #6447ef 0%, #8D6BFF 100%)';
});
eraserBtn.addEventListener('click', () => {
  penColor = '#ffffff';
  eraserBtn.style.background = '#8D6BFF';
  penBtn.style.background = 'linear-gradient(135deg, #6447ef 0%, #8D6BFF 100%)';
});
sizeSlider.addEventListener('input', (e) => penSize = parseInt(e.target.value));
undoBtn.addEventListener('click', () => {
  if (history.length > 1) {
    redoStack.push(history.pop());
    restoreState(history[history.length - 1]);
  }
});
redoBtn.addEventListener('click', () => {
  if (redoStack.length > 0) {
    const state = redoStack.pop();
    history.push(state);
    restoreState(state);
  }
});
resetBtn.addEventListener('click', () => {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  saveState();
});

canvas.addEventListener('mousedown', startDrawing);
canvas.addEventListener('mousemove', draw);
canvas.addEventListener('mouseup', stopDrawing);
canvas.addEventListener('mouseleave', stopDrawing);
canvas.addEventListener('touchstart', startDrawing);
canvas.addEventListener('touchmove', draw);
canvas.addEventListener('touchend', stopDrawing);

ctx.fillStyle = '#ffffff';
ctx.fillRect(0, 0, canvas.width, canvas.height);
saveState();

const gridContainer = document.getElementById('image-grid-container');
for (let i = 1; i <= 6; i++) {
  const img = document.createElement('img');
  img.src = `https://picsum.photos/seed/${i}/300/300`;
  gridContainer.appendChild(img);
}

// Generate button downloads the canvas image
generateBtn.addEventListener('click', () => {
  const link = document.createElement('a');
  link.download = 'drawing.png';
  link.href = canvas.toDataURL('image/png');
  link.click();
});

// Download button downloads all 6 images as a zip
downloadBtn.addEventListener('click', async () => {
  const zip = new JSZip();
  const imgs = gridContainer.querySelectorAll('img');

  for (let i = 0; i < imgs.length; i++) {
    const imgData = await fetch(imgs[i].src)
      .then(res => res.blob());
    zip.file(`image${i+1}.png`, imgData);
  }

  zip.generateAsync({ type: 'blob' }).then((content) => {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(content);
    a.download = 'images.zip';
    a.click();
  });
});

gridContainer.querySelectorAll('img').forEach(img => {
  img.addEventListener('click', () => {
    overlayImg.src = img.src;
    overlay.style.display = 'flex';
  });
});

closeOverlay.addEventListener('click', () => {
  overlay.style.display = 'none';
  overlayImg.src = '';
});

