const profilePic = document.getElementById("profilePic");
const formPicture = document.getElementById("picture");

formPicture.addEventListener("change", e => {
    profilePic.src = window.URL.createObjectURL(formPicture.files[0]);
});
