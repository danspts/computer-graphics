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

// Add here the rendering of your spaceship

// This is a sample box.
// const geometry = new THREE.BoxGeometry( 1, 1, 1 );
const material = new THREE.MeshBasicMaterial( {color: 0xaaaaaa} );
// const cube = new THREE.Mesh( geometry, material );
// scene.add( cube );


// This is the Hull
const cylinderGeometry = new THREE.CylinderGeometry( 2, 2, 6, 32 );
const cylinder = new THREE.Mesh( cylinderGeometry, material );
scene.add( cylinder );

// This defines the initial distance of the camera
const cameraTranslate = new THREE.Matrix4();
cameraTranslate.makeTranslation(0,0,5);
camera.applyMatrix4(cameraTranslate)

renderer.render( scene, camera );

const controls = new OrbitControls( camera, renderer.domElement );

let isOrbitEnabled = true;

const toggleOrbit = (e) => {
	if (e.key == "o"){
		isOrbitEnabled = !isOrbitEnabled;
	}
}

const toggleWireframe = (e) => {
	if (e.key == "w"){
		// scene.material.wireframe = !scene.material.wireframe;
		cylinder.material.wireframe = !cylinder.material.wireframe;
	}
}

document.addEventListener('keydown',toggleOrbit)
document.addEventListener('keydown',toggleWireframe)


//controls.update() must be called after any manual changes to the camera's transform
controls.update();

function animate() {

	requestAnimationFrame( animate );

	controls.enabled = isOrbitEnabled;
	controls.update();

	renderer.render( scene, camera );

}
animate()