// Configure marked.js options
marked.setOptions({
    gfm: true,
    breaks: true,
    smartLists: true,
    smartypants: true
  });


const eTitle0 = document.querySelector('#e-title-0');
const preTitle0 = document.querySelector('.pre-title-0');
console.log(preTitle0);

eTitle0.addEventListener('input', function() {
  const markdownText = eTitle0.value;
  const rawHtml = marked.parse(markdownText);
  const sanitizedHtml = DOMPurify.sanitize(rawHtml);
  preTitle0.innerHTML = sanitizedHtml;
});
  