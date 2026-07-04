function predict(){

let age = document.getElementById("age").value;
let bp = document.getElementById("bp").value;
let sugar = document.getElementById("sugar").value;
let cholesterol = document.getElementById("cholesterol").value;

console.log(age,bp,sugar,cholesterol);   

fetch("http://127.0.0.1:5000/predict",{
    method:"POST",
    headers:{
        "Content-Type":"application/json"
    },
    body: JSON.stringify({
        name: document.getElementById("name").value,
        age: age,
        bp: bp,
        sugar: sugar,
        cholesterol: cholesterol
    })
})
.then(response => response.json())

.then(data => {

console.log(data);

if(data.risk == 1){

document.getElementById("result").innerHTML="⚠ High Risk";

}
else{

document.getElementById("result").innerHTML="✅ Low Risk";

}
document.getElementById("recommendation").innerHTML =
"Recommendation: " + data.recommendation;

document.getElementById("score").innerHTML =
"Health Score : " + data.score + "/100";

document.getElementById("status").innerHTML =
"Status : " + data.status;

createChart(bp,sugar,cholesterol);

})

.catch(error=>{
console.log("Error:",error);
});

}



function createChart(bp,sugar,cholesterol){

const ctx=document.getElementById("healthChart");

new Chart(ctx,{
type:'bar',

data:{
labels:['BP','Sugar','Cholesterol'],

datasets:[{
label:'Health Indicators',
data:[bp,sugar,cholesterol]
}]
}

});

}