function onUploadOk(el) {
    let ret = el.contentWindow.document.querySelector("body").innerText;
    if (ret != "") { alert(ret); window.location.reload(); }
}
function onUpload(el) {
    let btn = document.querySelector("input[type=submit]"); btn.disabled = true; btn.value = "正在上传";
}