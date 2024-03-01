document.getElementById('copyButton').addEventListener('click', function () {
    var textarea = document.getElementById('text-inside');
    textarea.select();
    document.execCommand('copy');
});
