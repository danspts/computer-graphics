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

const material = new THREE.MeshPhongMaterial( {color: 0xaaaaaa} );
const hullMat = new THREE.MeshPhongMaterial( {color:0xd0e0e3} );
const windowMat = new THREE.MeshPhongMaterial( {color: 0x8e7cc3} );
windowMat.side = THREE.BackSide;
const coneMat = new THREE.MeshPhongMaterial( {color: 0xa64d79} );
const wingMat = new THREE.MeshPhongMaterial( {color: 0x16537e} );
wingMat.side = THREE.DoubleSide;

const ship = new THREE.Object3D()

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

const sphereGeometry = new THREE.SphereGeometry( 5, 32, 16 );
const sphere = new THREE.Mesh( sphereGeometry, material );


// const torusTranslate = new THREE.Matrix4();
// torusTranslate.makeTranslation(0,2,-2);
// ring_1.applyMatrix4(torusTranslate);
// torusTranslate.makeTranslation(0,0, -2);
// ring_2.applyMatrix4(torusTranslate);

planet.add( sphere );

// light
const light = new THREE.AmbientLight( 0xffffff ); // soft white light

// scene
scene.add( ship );
scene.add( planet );
scene.add( light );

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
		material.wireframe = !material.wireframe;
		hullMat.wireframe = !hullMat.wireframe;
		windowMat.wireframe = !windowMat.wireframe;
		coneMat.wireframe = !coneMat.wireframe;
		wingMat.wireframe = !wingMat.wireframe;
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