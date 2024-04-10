function changecolor(filename,filename2){
    console.log("Changing color to:", filename);
    let img = document.querySelector("#tshirt-front");
    let img2 = document.querySelector("#tshirt-back");
    console.log("Found img element:", img);
    img.setAttribute('src', filename);
    img2.setAttribute('src',filename2);
    console.log("Image source set successfully.");
} 
