const getElement = id => document.getElementById(id);
const getByClass = cls => document.querySelectorAll(cls);
const clickButton = id => getElement(id).click();

function addUser() {
    clickButton("deleteUserReset");
    getElement("deleteUserField").value = "";
    clickButton("addUserSubmit");
}

const submitAddUserButton = getElement("submitAddUserButton");
submitAddUserButton.addEventListener("click", addUser);
const submitDeleteUserButton = getElement("submitDeleteUserButton");
submitDeleteUserButton.addEventListener("click", deleteUser);

const displayUsername = [].slice.call(document.querySelectorAll('.display-username'));
let selectedUserID = null;
function selectAccount(userID, username) {
    selectedUserID = userID;
    for (let i in displayUsername) {
        displayUsername[i].textContent = username;
    }
    clickButton("deleteUserButton");
}

function viewUser(username, name, email, profilePic) {
    getElement("viewUserUsername").textContent = username;
    getElement("viewUserName").textContent = name;
    getElement("viewUserEmail").textContent = email;
    getElement("viewUserProfilePic").src = profilePic;
    clickButton("viewUserButton");
}

function deleteUser() {
    clickButton("addUserReset");
    clickButton("deleteUserReset");
    getElement("deleteUserField").value = selectedUserID;
    clickButton("deleteUserSubmit");
}


// Add click event to buttons
const viewButtons = document.querySelectorAll(".view-button");
const deleteButton = document.querySelectorAll(".delete-button");
const names = document.querySelectorAll(".user-details-name");
const usernames = document.querySelectorAll(".user-details-username");
const emails = document.querySelectorAll(".user-details-email");
const profilePics = document.querySelectorAll(".user-details-profile-pic");
const userIDs = document.querySelectorAll(".user-details-user-id");

for (let i=0; i < viewButtons.length; i++) {
    viewButtons[i].addEventListener("click", e => {
        viewUser(usernames[i].textContent, names[i].textContent, emails[i].textContent, profilePics[i].textContent);
    });
    deleteButton[i].addEventListener("click", e => {
        selectAccount(userIDs[i].textContent, usernames[i].textContent);
    });
}
