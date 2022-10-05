var CandidateList = new candidateList();

function addCandidate() {
  // get data from input
  var first_name = document.getElementById("first_name").value;
  var last_name = document.getElementById("last_name").value;
  var email = document.getElementById("email").value;
  var getValue = document.getElementById("jobchosen");
  var position = getValue.options[getValue.selectedIndex].value;
  console.log(position);
  var phone = document.getElementById("phone").value;

  //add student

  var Candidate = new candidate(first_name, last_name, email, phone, position);
  CandidateList.addCandidate(Candidate);
}

function saveStorage() {
  addCandidate();
  var jsonCandidateList = JSON.stringify(CandidateList.list);
  localStorage.setItem("candidateList", jsonCandidateList);
}

function updateStudentList(studentLst) {
  var lstTable = document.querySelector("#tbodyCandidate");
  lstTable.innerHTML = "";
  for (var i = 0; i < studentLst.list.length; i++) {
    var student = studentLst.list[i];
    var trStudent = document.createElement("tr");
    var tdCheckBox = document.createElement("td");
    var tdID = createTdStudent("studentID", student.StudentID);
    var tdName = createTdStudent("studentName", student.StudentName);
    var tdEmail = createTdStudent("email", student.email);
    var tdPhone = createTdStudent("phone", student.phone);
    var tdIdentity = createTdStudent("identityNumber", student.identityNo);

    trStudent.appendChild(tdCheckBox);
    trStudent.appendChild(tdID);
    trStudent.appendChild(tdName);
    trStudent.appendChild(tdEmail);
    trStudent.appendChild(tdPhone);
    trStudent.appendChild(tdIdentity);

    lstTable.appendChild(trStudent);
    console.log(i);
  }
}

function createTdStudent(className, value) {
  var td = document.createElement("td");
  td.className = className;
  td.innerHTML = value;
  return td;
}

function getStorage() {
  var jsonStudentList = localStorage.getItem("studentList");
  var studentArr = JSON.parse(jsonStudentList);
  studentList.list = studentArr;
  updateStudentList(studentList);
}

document.getElementById("submitApp").onclick = saveStorage;
