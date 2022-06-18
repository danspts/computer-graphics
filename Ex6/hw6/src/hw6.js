// Scene Declartion
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera( 75, window.innerWidth / window.innerHeight, 0.1, 1000 );

const renderer = new THREE.WebGLRenderer();
renderer.setSize( window.innerWidth, window.innerHeight );
document.body.appendChild( renderer.domElement );


// helper function for later on
function degrees_to_radians(degrees)
{
  var pi = Math.PI;
  return degrees * (pi/180);
}


// Constants
const NB_WINGS = 6;
const INV_SCALE_FACTOR = 5;


// Here we load the cubemap and skymap, you may change it

const loader = new THREE.CubeTextureLoader();
const texture = loader.load([
  'src/skybox/right.png',
  'src/skybox/left.png',
  'src/skybox/top.png',
  'src/skybox/bottom.png',
  'src/skybox/front.png',
  'src/skybox/back.png',
]);
scene.background = texture;


// TODO: Texture Loading
// We usually do the texture loading before we start everything else, as it might take processing time
const textureLoader = new THREE.TextureLoader();

const earthTex = textureLoader.load('src/textures/earth.jpg');
const moonTex = textureLoader.load('src/textures/moon.jpg');
const starTex = textureLoader.load('src/textures/star.jpg');


// Materials
const hullMat = new THREE.MeshPhongMaterial({ color: 0xd0e0e3 });
const windowMat = new THREE.MeshPhongMaterial({ color: 0x8e7cc3 });
windowMat.side = THREE.BackSide;
const coneMat = new THREE.MeshPhongMaterial({ color: 0xa64d79 });
const wingMat = new THREE.MeshPhongMaterial({ color: 0x16537e });
wingMat.side = THREE.DoubleSide;
// hullMat.wireframe = true;
const moonMat = new THREE.MeshPhongMaterial({ map: moonTex });
const earthMat = new THREE.MeshPhongMaterial({ map: earthTex });
// earthMat.wireframe = true;

var materials = [earthMat, moonMat, hullMat, windowMat, coneMat, wingMat]


// TODO: Spaceship
// You should copy-paste the spaceship from the previous exercise here

// Objects
const ship = new THREE.Object3D()

// Hull
const hull = new THREE.Object3D()
ship.add(hull)

const cylinderGeometry = new THREE.CylinderGeometry(2, 2, 6, 32);
const cylinder = new THREE.Mesh(cylinderGeometry, hullMat);
ship.add(cylinder);

// Ship's head
const coneGeometry = new THREE.ConeGeometry(2, 2, 32);
const cone = new THREE.Mesh(coneGeometry, coneMat);
const coneTranslate = new THREE.Matrix4();
coneTranslate.makeTranslation(0, 4, 0);
cone.applyMatrix4(coneTranslate);
ship.add(cone);

// Windows 
const ringGeometry = new THREE.RingGeometry(0.5, 0.75, 16, 100);
const ring_1 = new THREE.Mesh(ringGeometry, windowMat);
const ring_2 = ring_1.clone();
const torusTranslate = new THREE.Matrix4();
torusTranslate.makeTranslation(0, 2, -2);
ring_1.applyMatrix4(torusTranslate);
torusTranslate.makeTranslation(0, 0, -2);
ring_2.applyMatrix4(torusTranslate);


hull.add(ring_1);
hull.add(ring_2);

// Wings
const shape = new THREE.Shape();
const x = -2;
const y = 0;
shape.moveTo(x - 2, y - 3);
shape.lineTo(x, y - 3);
shape.lineTo(x, y);
const TriangleGeometry = new THREE.ShapeGeometry(shape);
const wingRotate = new THREE.Matrix4();
[...Array(NB_WINGS).keys()].map(function (i) {
	let wing_ob = new THREE.Mesh(TriangleGeometry, wingMat);
	wingRotate.makeRotationY(i * 2 * Math.PI / NB_WINGS);
	wing_ob.applyMatrix4(wingRotate);
	ship.add(wing_ob);
})

// Propelers 
const geometryPropelers = new THREE.CylinderGeometry( 1, 2, 3, 32 );
const properler = new THREE.Mesh(geometryPropelers, wingMat);


// TODO: Planets
// You should add both earth and the moon here
const planets = new THREE.Object3D()

// Moon
const moon = new THREE.Object3D()
planets.add(moon)
let radius = 5 * (coneGeometry.parameters.height + cylinderGeometry.parameters.height)
const moonSphereGeometry = new THREE.SphereGeometry(radius/3, 32, 16);
const moonSphere = new THREE.Mesh(moonSphereGeometry, moonMat);
moon.add(moonSphere);

// Earth
const earth = new THREE.Object3D()
planets.add(earth)
const earthSphereGeometry = new THREE.SphereGeometry(radius, 32, 16);
const earthSphere = new THREE.Mesh( earthSphereGeometry, earthMat);
const earthTranslateMatrix = new THREE.Matrix4();
earthTranslateMatrix.makeTranslation(100,5,100);
earthSphere.applyMatrix4(earthTranslateMatrix);
earth.add(earthSphere);

// TODO: remove later
// const ballgeo = new THREE.SphereGeometry(1,32,16);
// const ball = new THREE.Mesh(ballgeo, moonMat);
// const ballmove = new THREE.Matrix4();
// ballmove.makeTranslation(0,10,0);
// ball.applyMatrix4(ballmove);




// TODO: Bezier Curves


// TODO: Camera Settings
// Set the camera following the spaceship here


// TODO: Add collectible stars


// TODO: Add Lighting


// Directional Light
const sunLight = new THREE.DirectionalLight( 0xffffff, 0.5 );
const translateSun = new THREE.Matrix4();
translateSun.makeTranslation(0,-10,10);
sunLight.applyMatrix4(translateSun);
sunLight.target = planets;

// Spotlight
const spotLight = new THREE.SpotLight( 0xffffff );
spotLight.position.set( 0, 6, 0 );
ship.add(spotLight);

const spotTarget = new THREE.Object3D();
spotLight.target = spotTarget;
const translateTarget = new THREE.Matrix4();
translateTarget.makeTranslation(0,10,0);
spotTarget.applyMatrix4(translateTarget);
ship.add(spotTarget);

// light placeholder
const hemiLight = new THREE.HemisphereLight(0xffffff, 0xffffff, 0.7);
hemiLight.color.setHSL(0.6, 1, 0.6);
hemiLight.groundColor.setHSL(0.095, 1, 1);
hemiLight.position.set(0, 0, -10);


// Scene
scene.add(ship);
scene.add(hemiLight);
scene.add(planets);
scene.add(sunLight);
// scene.add(ball);


// placing the camera at a distance
// TODO: this wasn't in the file, this is just for debugging! remove later
const cameraTranslate = new THREE.Matrix4();
// cameraTranslate.makeTranslation(0, 0, 2 * radius );
// cameraTranslate.makeTranslation(0, 0, radius );
cameraTranslate.makeTranslation(100,5,100 + 2 * radius);
const cameraRotate = new THREE.Matrix4();
cameraRotate.makeRotationY(degrees_to_radians(-60));
camera.applyMatrix4(cameraTranslate)
camera.applyMatrix4(cameraRotate)
renderer.render(scene, camera);


// TODO: Add keyboard event
// We wrote some of the function for you
const handle_keydown = (e) => {
	if(e.code == 'ArrowLeft'){
		// TODO
	} else if (e.code == 'ArrowRight'){
		// TODO
	}
}
document.addEventListener('keydown', handle_keydown);



function animate() {

	requestAnimationFrame( animate );

	// TODO: Animation for the spaceship position


	// TODO: Test for star-spaceship collision

	
	renderer.render( scene, camera );

}
animate()