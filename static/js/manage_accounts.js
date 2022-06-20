const getElement = id => document.getElementById(id);
const clickButton = id => getElement(id).click();

function addUser() {
    clickButton("deleteUserReset");
    getElement("deleteUserField").value = "";
    clickButton("addUserSubmit");
}

const displayUsername = [].slice.call(document.querySelectorAll('.display-username'));
let selectedUserID = null;
function selectAccount(userID, username, buttonID) {
    selectedUserID = userID;
    for (let i in displayUsername) {
        displayUsername[i].innerText = username;
    }
    clickButton(buttonID);
}

function viewUser(username, name, email, profilePic) {
    getElement("viewUserUsername").innerText = username;
    getElement("viewUserName").innerText = name;
    getElement("viewUserEmail").innerText = email;
    getElement("viewUserProfilePic").src = profilePic;
    clickButton("viewUserButton");
}

function deleteUser() {
    clickButton("addUserReset");
    clickButton("deleteUserReset");
    getElement("deleteUserField").value = selectedUserID;
    clickButton("deleteUserSubmit");
}
