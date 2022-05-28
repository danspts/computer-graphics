import {OrbitControls} from './OrbitControls.js'

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera( 75, window.innerWidth / window.innerHeight, 0.1, 1000 );

const renderer = new THREE.WebGLRenderer();
renderer.setSize( window.innerWidth, window.innerHeight );
document.body.appendChild( renderer.domElement );

function degrees_to_radians(degrees)
{
  var pi = Math.PI;
  return degrees * (pi/180);
}

var textureURL = "https://s3-us-west-2.amazonaws.com/s.cdpn.io/17271/lroc_color_poles_1k.jpg"; 
var displacementURL = "https://s3-us-west-2.amazonaws.com/s.cdpn.io/17271/ldem_3_8bit.jpg"; 
var worldURL = "https://s3-us-west-2.amazonaws.com/s.cdpn.io/17271/hipp8_s.jpg"

var textureLoader = new THREE.TextureLoader();
var texture = textureLoader.load( textureURL );
var displacementMap = textureLoader.load( displacementURL );
var worldTexture = textureLoader.load( worldURL );

var moonMaterial = new THREE.MeshPhongMaterial ( 
  { color: 0xffffff ,
  map: texture ,
     displacementMap: displacementMap,
  displacementScale: 0.06,
  bumpMap: displacementMap,
  bumpScale: 0.04,
   reflectivity:0, 
   shininess :0
  } 

);


var worldGeometry = new THREE.SphereGeometry( 1000,60,60 );
var worldMaterial = new THREE.MeshBasicMaterial ( 
  { color: 0xffffff ,
  map: worldTexture ,
  side: THREE.BackSide
  } 
);
var world = new THREE.Mesh( worldGeometry, worldMaterial );

// Add here the rendering of your spaceship

const material = new THREE.MeshPhongMaterial( {color: 0xaaaaaa} );
const hullMat = new THREE.MeshPhongMaterial( {color:0xd0e0e3} );
const windowMat = new THREE.MeshPhongMaterial( {color: 0x8e7cc3} );
windowMat.side = THREE.BackSide;
const coneMat = new THREE.MeshPhongMaterial( {color: 0xa64d79} );
const wingMat = new THREE.MeshPhongMaterial( {color: 0x16537e} );
wingMat.side = THREE.DoubleSide;

const orbit = new THREE.Object3D()
const ship = new THREE.Object3D()
orbit.add(ship)

// Hull
const hull = new THREE.Object3D()
ship.add(hull)

const cylinderGeometry = new THREE.CylinderGeometry( 2, 2, 6, 32 );
const cylinder = new THREE.Mesh( cylinderGeometry, hullMat );
ship.add( cylinder );

const coneGeometry = new THREE.ConeGeometry( 2, 2, 32 );
const cone = new THREE.Mesh( coneGeometry, coneMat );

const coneTranslate = new THREE.Matrix4();
coneTranslate.makeTranslation(0,4,0);
cone.applyMatrix4(coneTranslate);

hull.add( cone );

// Windows 
const ringGeometry = new THREE.RingGeometry( 0.5, 0.75, 16, 100 );
const ring_1 = new THREE.Mesh( ringGeometry, windowMat );
const ring_2 = ring_1.clone();

const torusTranslate = new THREE.Matrix4();
torusTranslate.makeTranslation(0,2,-2);
ring_1.applyMatrix4(torusTranslate);
torusTranslate.makeTranslation(0,0, -2);
ring_2.applyMatrix4(torusTranslate);

hull.add( ring_1 );
hull.add( ring_2 );

// Wings
const shape = new THREE.Shape();

const x = -2;
const y = 0;

shape.moveTo(x - 2, y - 3);
shape.lineTo(x, y - 3);
shape.lineTo(x, y);

const TriangleGeometry = new THREE.ShapeGeometry(shape);

const nbWings = 6;

const wingRotate = new THREE.Matrix4();

[...Array(nbWings).keys()].map(i => [i, new THREE.Mesh( TriangleGeometry, wingMat )])
.map(function([i, wing_ob]){
	wingRotate.makeRotationY(i * 2 * Math.PI / nbWings);
	wing_ob.applyMatrix4(wingRotate);
	return wing_ob;
})
.map(elem => ship.add(elem));

// Planet
const planet = new THREE.Object3D()
orbit.add(planet)


const sphereGeometry = new THREE.SphereGeometry( 5, 32, 16 );
const sphere = new THREE.Mesh( sphereGeometry, moonMaterial );

const shipTranslate = new THREE.Matrix4();
shipTranslate.makeTranslation(10,0,0);
ship.applyMatrix4(shipTranslate);

planet.add( sphere );

// light
const hemiLight = new THREE.HemisphereLight( 0xffffff, 0xffffff, 0.7 );
hemiLight.color.setHSL( 0.6, 1, 0.6 );
hemiLight.groundColor.setHSL( 0.095, 1, 1 );
hemiLight.position.set( 0, 0, -10 );

// orbit translated since moon cannot be at the center
const orbitTranslate = new THREE.Matrix4();
orbitTranslate.makeTranslation(-4,5,2);
orbit.applyMatrix4(orbitTranslate)

// orbit tranformation matrices
// for animation '1' - rotate around the X axis
const anim1Translate = new THREE.Matrix4();
anim1Translate.makeTranslation(0,orbit.position.y,0);
const anim1Rotate = new THREE.Matrix4();
anim1Rotate.makeRotationY(degrees_to_radians(1));
let anim1 = new THREE.Matrix4().identity();
anim1.multiply(anim1Translate);
anim1.multiply(anim1Rotate);
anim1.multiply(anim1Translate.invert());

// for animation '2' - rotate around the Y axis
const anim2Translate = new THREE.Matrix4();
anim2Translate.makeTranslation(orbit.position.x,0,0);
const anim2Rotate = new THREE.Matrix4();
anim2Rotate.makeRotationX(degrees_to_radians(-1));
let anim2 = new THREE.Matrix4().identity();
anim2.multiply(anim2Translate);
anim2.multiply(anim2Rotate);
anim2.multiply(anim2Translate.invert());

// scene
scene.add(orbit);
scene.add( world );
scene.add( hemiLight );


// This defines the initial distance of the camera
const cameraTranslate = new THREE.Matrix4();
cameraTranslate.makeTranslation(0,0,5);
camera.applyMatrix4(cameraTranslate)

renderer.render( scene, camera );

const controls = new OrbitControls( camera, renderer.domElement );

let isOrbitEnabled = true;
let isAnim1Enabled = false;
let isAnim2Enabled = false;

const toggleOrbit = (e) => {
	if (e.key == "o"){
		isOrbitEnabled = !isOrbitEnabled;
	}
}

const toggleWireframe = (e) => {
	if (e.key == "w"){
		// scene.material.wireframe = !scene.material.wireframe;
		material.wireframe = !material.wireframe;
		hullMat.wireframe = !hullMat.wireframe;
		windowMat.wireframe = !windowMat.wireframe;
		coneMat.wireframe = !coneMat.wireframe;
		wingMat.wireframe = !wingMat.wireframe;
		moonMaterial.wireframe = !moonMaterial.wireframe;
	}
}

const toggleAnim1 = (e) => {
	if (e.key == "1"){
		isAnim1Enabled = !isAnim1Enabled;
	}
}

const toggleAnim2 = (e) => {
	if (e.key == "2"){
		isAnim2Enabled = !isAnim2Enabled;
	}
}

document.addEventListener('keydown',toggleOrbit)
document.addEventListener('keydown',toggleWireframe)
document.addEventListener('keydown',toggleAnim1)
document.addEventListener('keydown',toggleAnim2)


//controls.update() must be called after any manual changes to the camera's transform
controls.update();

function animate() {

	requestAnimationFrame( animate );

	controls.enabled = isOrbitEnabled;
	controls.update();

	if (isAnim1Enabled){
		ship.applyMatrix4(anim1);
	}

	if (isAnim2Enabled){
		ship.applyMatrix4(anim2);
	}

	renderer.render( scene, camera );

}
animate()