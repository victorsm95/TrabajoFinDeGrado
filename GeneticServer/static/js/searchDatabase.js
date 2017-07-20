//FUNCION ENCARGADA DE OBTENER LA INFORMACION DE CADA GEN (MOSTRANDO LA FUNCION DE LOS MISMOS)
function requestInfoGen(name) {
  var x = name;
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      document.getElementById("infoGenes").innerHTML = '<div class="well">' + '<center><strong>Function of gen ' + name + '</center></strong>' + this.responseXML.getElementsByTagName("comment")[0].getElementsByTagName("text")[0].childNodes[0].nodeValue + '</div>';
    }
  };
  xhttp.open("GET", "http://www.uniprot.org/uniprot/?query=".concat(x.concat('+AND+organism:9606&sort=score&limit=1&format=xml')), true);
  xhttp.send();
} 

//MUESTRA LA FUNCION DEL GEN CUYO NOMBRE SE PASA COMO PARAMETRO
function showInfoGen(name) {
  
  requestInfoGen(name);
}

//OCULTA LA FUNCION DEL GEN
function hiddenInfoGen() {
  document.getElementById("infoGenes").innerHTML = '';
}
