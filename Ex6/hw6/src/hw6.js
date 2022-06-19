// Scene Declartion
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);

const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// helper function for later on
function degrees_to_radians(degrees) {
	var pi = Math.PI;
	return degrees * (pi / 180);
}

function mod(n, m) {
	let remainder = n % m;
	return remainder >= 0 ? remainder : remainder + m;
}

// Constants and Predefined Values
const NB_WINGS = 6;
const INV_SCALE_FACTOR = 5;
const NUM_POINTS = 3000;
const COLLISION_EPSILON = 0.025;
const SPEED_COEFFICIENT = 1.2;
const INV_SPEED_COEFFICIENT = 1 / SPEED_COEFFICIENT;
let speed = 1;
let t = 0;
let curveNum = 0;
let collected = 0;
let clock = new THREE.Clock();
let delta = 0;
let fps = 1 / 60;


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
const starMat = new THREE.MeshPhongMaterial({ map: starTex });

var materials = [starMat, earthMat, moonMat, hullMat, windowMat, coneMat, wingMat]


// TODO: Spaceship
// You should copy-paste the spaceship from the previous exercise here
const shipTrajectory = new THREE.Object3D();

// Objects
const ship = new THREE.Object3D();
shipTrajectory.add(ship);

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
const geometryPropelers = new THREE.CylinderGeometry(1, 2, 3, 32);
const properler = new THREE.Mesh(geometryPropelers, wingMat);


// TODO: Planets
// You should add both earth and the moon here
const planets = new THREE.Object3D()

// Moon
const moon = new THREE.Object3D()
planets.add(moon)
let radius = 5 * (coneGeometry.parameters.height + cylinderGeometry.parameters.height)
const moonSphereGeometry = new THREE.SphereGeometry(radius / 3, 32, 16);
const moonSphere = new THREE.Mesh(moonSphereGeometry, moonMat);
moon.add(moonSphere);

// Earth
const earth = new THREE.Object3D()
planets.add(earth)
const earthSphereGeometry = new THREE.SphereGeometry(radius, 32, 16);
const earthSphere = new THREE.Mesh(earthSphereGeometry, earthMat);
const earthTranslateMatrix = new THREE.Matrix4();
earthTranslateMatrix.makeTranslation(100, 5, 100);
earthSphere.applyMatrix4(earthTranslateMatrix);
earth.add(earthSphere);

// TODO: remove later
// const ballgeo = new THREE.SphereGeometry(1,32,16);
// const ball = new THREE.Mesh(ballgeo, moonMat);
// const ballmove = new THREE.Matrix4();
// ballmove.makeTranslation(0,10,0);
// ball.applyMatrix4(ballmove);


// TODO: Add Lighting

// Directional Light
const sunLight = new THREE.DirectionalLight(0xffffff, 0.5);
const translateSun = new THREE.Matrix4();
translateSun.makeTranslation(0, -10, 10);
sunLight.applyMatrix4(translateSun);
sunLight.target = planets;

// Spotlight
const spotLight = new THREE.SpotLight(0xffffff);
spotLight.position.set(0, 6, 0);
ship.add(spotLight);

const spotTarget = new THREE.Object3D();
spotLight.target = spotTarget;
const translateTarget = new THREE.Matrix4();
translateTarget.makeTranslation(0, 10, 0);
spotTarget.applyMatrix4(translateTarget);
ship.add(spotTarget);

// light placeholder
const hemiLight = new THREE.HemisphereLight(0xffffff, 0xffffff, 0.7);
hemiLight.color.setHSL(0.6, 1, 0.6);
hemiLight.groundColor.setHSL(0.095, 1, 1);
hemiLight.position.set(-5, -5, 22)


// Moving the Ship Outside the Moon
const shipTranslate = new THREE.Matrix4();
shipTranslate.makeTranslation(radius / 3 + 10, 0, 0);
shipTrajectory.applyMatrix4(shipTranslate);

let curves = [];
// TODO: Bezier Curves
const routes = new THREE.Object3D();
// TODO: remove later, this is just for visualizing
const curveMat = new THREE.LineBasicMaterial({ color: 0xff0000 });

// Route A
const curveA = new THREE.QuadraticBezierCurve3(
	shipTrajectory.position,
	new THREE.Vector3(0, 5, 40),
	new THREE.Vector3(100, 10 + radius + 5, -10 - radius + 100)
);

const pointsA = curveA.getPoints(3000);
const curveAGeometry = new THREE.BufferGeometry().setFromPoints(pointsA);
const routeA = new THREE.Line(curveAGeometry, curveMat);
routes.add(routeA);
curves.push(curveA);

// Route B
const curveB = new THREE.QuadraticBezierCurve3(
	shipTrajectory.position,
	new THREE.Vector3(50, 0, 50),
	new THREE.Vector3(100, 10 + radius + 5, -10 - radius + 100)
);

const pointsB = curveB.getPoints(3000);
const curveBGeometry = new THREE.BufferGeometry().setFromPoints(pointsB);
const routeB = new THREE.Line(curveBGeometry, curveMat);
routes.add(routeB);
curves.push(curveB);

// Route C
const curveC = new THREE.QuadraticBezierCurve3(
	shipTrajectory.position,
	new THREE.Vector3(70, -5, 70),
	new THREE.Vector3(100, 10 + radius + 5, -10 - radius + 100)
);

const pointsC = curveC.getPoints(3000);
const curveCGeometry = new THREE.BufferGeometry().setFromPoints(pointsC);
const routeC = new THREE.Line(curveCGeometry, curveMat);
routes.add(routeC);
curves.push(curveC);

var curveList = curves.map(curve => curve.getSpacedPoints(NUM_POINTS));
const lenCurveList = curveList.length;

// TODO: Camera Settings
// Set the camera following the spaceship here
const cameraTranslate = new THREE.Matrix4();
cameraTranslate.makeTranslation(shipTrajectory.position.x, shipTrajectory.position.y - 5, shipTrajectory.position.z - 20);
const cameraRotateY = new THREE.Matrix4();
cameraRotateY.makeRotationY(degrees_to_radians(-20));
const cameraRotateX = new THREE.Matrix4();
cameraRotateX.makeRotationX(degrees_to_radians(180));
const cameraRotateZ = new THREE.Matrix4();
cameraRotateZ.makeRotationZ(degrees_to_radians(60));
camera.applyMatrix4(cameraRotateY)
camera.applyMatrix4(cameraRotateX)
camera.applyMatrix4(cameraRotateZ)
camera.applyMatrix4(cameraTranslate)

// TODO: Add collectible stars
const stars = new THREE.Object3D();

const starGeometry = new THREE.DodecahedronGeometry();
const starObject = new THREE.Mesh(starGeometry, starMat);
class Star {


	constructor(curveList) {
		let randInt = ~~(Math.random() * NUM_POINTS)
		let space = curveList[~~(Math.random() * curveList.length)]
		let v = space[randInt];
		let starTranslate = new THREE.Matrix4();
		starTranslate.makeTranslation(v.x, v.y, v.z);
		this.tValue = randInt / NUM_POINTS;
		this.starObj = starObject.clone();
		this.starObj.applyMatrix4(starTranslate);
	}
}

let star_obj = new Star(curveList);

stars.add(star_obj.starObj);

var starList = [star_obj];


// Scene
scene.add(shipTrajectory);
// scene.add(ship);
scene.add(hemiLight);
scene.add(planets);
scene.add(sunLight);
scene.add(routes);
scene.add(stars);
// scene.add(ball);

// TODO: Add keyboard event
// We wrote some of the function for you
const handle_keydown = (e) => {
	switch (e.code) {
		case 'ArrowLeft':
			curveNum = mod(curveNum + 1, lenCurveList);
			break;
		case 'ArrowRight':
			curveNum = mod(curveNum - 1, lenCurveList);
			break;
	}
}

const handle_speed = (e) => {
	switch (e.code) {
		case 'ArrowUp':
			speed *= SPEED_COEFFICIENT;
			break;
		case 'ArrowDown':
			speed *= INV_SPEED_COEFFICIENT;
			break;
	}
}

document.addEventListener('keydown', handle_speed);
document.addEventListener('keydown', handle_keydown);

ship.rotation.x = Math.PI / 2;

function animate() {

	requestAnimationFrame(animate);


	// TODO: Animation for the spaceship position
	if (t < NUM_POINTS) {
		let pointList = curveList[curveNum];
		let newPos = pointList[t];
		shipTrajectory.lookAt(pointList[t])
		newPos.addScaledVector(shipTrajectory.position, -1);
		let posTranslate = new THREE.Matrix4();
		posTranslate.makeTranslation(newPos.x, newPos.y, newPos.z);
		shipTrajectory.applyMatrix4(posTranslate);
		camera.applyMatrix4(posTranslate);
		t += Math.max(1, Math.floor(speed));
	}

	// TODO: Test for star-spaceship collision
	if (starList.length > 0 && Math.abs(starList[0].tValue - (t - 1) / NUM_POINTS) < COLLISION_EPSILON) {
		if (starList[0].curveIndex == curveNum) {
			collected += 1;
			starList[0].starObj.visible = false;
			starList.shift();
		}
	}
	delta += clock.getDelta();

	if (delta > fps) {
		renderer.render(scene, camera);
		delta = delta % fps;
	}


}
animate()