const b64 = (s) => s.replace(/-/g, "+");
document.querySelector("p").textContent = b64("a-b");
