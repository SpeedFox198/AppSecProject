const field = document.getElementById("bookCoverField");
const bookcover = document.getElementById("bookcover");

field.addEventListener("change", e => {
    bookcover.src = window.URL.createObjectURL(field.files[0]);
    bookcover.classList.remove("d-none");
});
