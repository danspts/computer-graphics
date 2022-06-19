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
const NB_STARS = 5;
const NB_BAD_STARS = 3;
const INV_SCALE_FACTOR = 5;
const NUM_POINTS = 3000;
const COLLISION_EPSILON = NUM_POINTS / 150;
const SPEED_COEFFICIENT = 1.2;
const INV_SPEED_COEFFICIENT = 1 / SPEED_COEFFICIENT;
let speed = 1;
let t = 0;
let curveNum = 0;
let collected = 0;
let clock = new THREE.Clock();
let delta = 0;
let fps = 1 / 60;


var moonTextureURL = "https://s3-us-west-2.amazonaws.com/s.cdpn.io/17271/lroc_color_poles_1k.jpg";
var moonDisplacementURL = "https://s3-us-west-2.amazonaws.com/s.cdpn.io/17271/ldem_3_8bit.jpg";
var earthTextureURL = "https://raw.githubusercontent.com/turban/webgl-earth/master/images/2_no_clouds_4k.jpg"
var earthDisplacementURL = "https://raw.githubusercontent.com/turban/webgl-earth/master/images/elev_bump_4k.jpg"
var earthSpecularURL = "https://raw.githubusercontent.com/turban/webgl-earth/master/images/water_4k.png"
var earthCloudsURL = "https://raw.githubusercontent.com/turban/webgl-earth/master/images/fair_clouds_4k.png"
var badStarTextureURL = "https://i.imgur.com/jJZZUHl.jpeg";

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

const textureLoader = new THREE.TextureLoader();
const earthTexture = textureLoader.load(earthTextureURL);
const earthDisplacementMap = textureLoader.load(earthDisplacementURL);
const earthSpecular = textureLoader.load(earthSpecularURL);
const earthCloudsTexture = textureLoader.load(earthCloudsURL);

const moonTexture = textureLoader.load(moonTextureURL);
const moonDisplacementMap = textureLoader.load(moonDisplacementURL);
const badStarTexture = textureLoader.load(badStarTextureURL);
const starTexture = textureLoader.load('src/textures/star.jpg');


// Materials
const hullMat = new THREE.MeshPhongMaterial({ color: 0xd0e0e3 });
const windowMat = new THREE.MeshPhongMaterial({ color: 0x8e7cc3 });
windowMat.side = THREE.BackSide;
const coneMat = new THREE.MeshPhongMaterial({ color: 0xa64d79 });
const wingMat = new THREE.MeshPhongMaterial({ color: 0x16537e });
wingMat.side = THREE.DoubleSide;
const moonMat = new THREE.MeshPhongMaterial(
	{
		color: 0xffffff,
		map: moonTexture,
		displacementMap: moonDisplacementMap,
		displacementScale: 0.06,
		bumpMap: moonDisplacementMap,
		bumpScale: 0.07,
		reflectivity: 0,
		shininess: 0
	}

);
const earthMat = new THREE.MeshPhongMaterial(
	{
		color: 0xffffff,
		map: earthTexture,
		displacementMap: earthDisplacementMap,
		displacementScale: 0.5,
		bumpMap: earthDisplacementMap,
		bumpScale: 0.5,
		specularMap: earthSpecular,
		specular: new THREE.Color('grey')
	}

);
const earthCloudsMat = new THREE.MeshPhongMaterial({
	map: earthCloudsTexture,
	transparent: true
})

const starMat = new THREE.MeshPhongMaterial({
	map: starTexture,
	displacementMap: moonDisplacementMap,
	displacementScale: 2,
	bumpMap: moonDisplacementMap,
	bumpScale: 2,
	reflectivity: 0,
	shininess: 0
});

const badStarMat = new THREE.MeshPhongMaterial({
	map: badStarTexture,
	displacementMap: moonDisplacementMap,
	displacementScale: 2,
	bumpMap: moonDisplacementMap,
	bumpScale: 2,
	reflectivity: 0,
	shininess: 0
});

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
const earthCloudsGeometry = new THREE.SphereGeometry(radius + 1.5, 32, 16);
const earthClouds = new THREE.Mesh(earthCloudsGeometry, earthCloudsMat);
earthClouds.applyMatrix4(earthTranslateMatrix);
earth.add(earthClouds);
earth.add(earthSphere);


let planetList = [earthSphere, moonSphere]

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
// Bezier Curves
const routes = new THREE.Object3D();
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

// Camera Settings
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

// Collectible stars
const stars = new THREE.Object3D();

const starGeometry = new THREE.DodecahedronGeometry(1, 1);
const starObject = new THREE.Mesh(starGeometry, starMat);
const badStarObject = new THREE.Mesh(starGeometry, badStarMat);

class Star {
	constructor(curveList, isGood = true) {
		this.isGood = isGood
		let randInt = ~~(Math.random() * NUM_POINTS)
		this.space = curveList[~~(Math.random() * curveList.length)]
		let v = this.space[randInt];
		let starRotate = new THREE.Matrix4().identity();
		starRotate.multiply(new THREE.Matrix4().makeTranslation(v.x, v.y, v.z));
		starRotate.multiply(new THREE.Matrix4().makeRotationX(Math.random() * 2 - 1));
		starRotate.multiply(new THREE.Matrix4().makeRotationY(Math.random() * 2 - 1));
		starRotate.multiply(new THREE.Matrix4().makeRotationZ(Math.random() * 2 - 1));
		this.tValue = randInt / NUM_POINTS;
		if (isGood) this.starObj = starObject.clone();
		else this.starObj = badStarObject.clone();
		this.starObj.applyMatrix4(starRotate);
	}
}

var starList = [...Array(NB_STARS)].map(_ => new Star(curveList, true));
starList = starList.concat([...Array(NB_BAD_STARS)].map(_ => new Star(curveList, false)));
starList.forEach(star => stars.add(star.starObj));

// Scene
scene.add(shipTrajectory);
scene.add(hemiLight);
scene.add(planets);
scene.add(sunLight);
scene.add(routes);
scene.add(stars);

const handle_keydown = (e) => {
	console.log(curveNum)
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

let shipAlign = new THREE.Matrix4().identity();
shipAlign.multiply(new THREE.Matrix4().makeTranslation(ship.position.x, ship.position.y, ship.position.z));
shipAlign.multiply(new THREE.Matrix4().makeRotationX(Math.PI / 2));
shipAlign.multiply(new THREE.Matrix4().makeTranslation(-ship.position.x, -ship.position.y, -ship.position.z));
ship.applyMatrix4(shipAlign);

var score = document.createElement('div');
score.style.position = 'absolute';
score.style.width = 100;
score.style.height = 100;
score.style.color = "white";
score.style.top = 50 + 'px';
score.style.left = 50 + 'px';
document.body.appendChild(score);

var time = document.createElement('div');
time.style.position = 'absolute';
time.style.width = 100;
time.style.height = 100;
time.style.color = "white";
time.style.top = 50 + 'px';
time.style.right = 50 + 'px';
document.body.appendChild(time);
let clockTime = 0;

var promptMsg = document.createElement('div');
promptMsg.style.position = 'absolute';
promptMsg.style.zIndex = 1;
promptMsg.style.width = 1000;
promptMsg.style.height = 1000;
promptMsg.style.color = "black";
promptMsg.style.top = 50 + '%';
promptMsg.style.right = 30 + '%';
promptMsg.style.left = 30 + '%';
promptMsg.style.fontSize = 300 + '%';
promptMsg.style.textAlign = 'center';
promptMsg.style.backgroundColor = 'yellow';
promptMsg.style.fontweight = 'bold';
promptMsg.style.fontFamily = 'Lucida Handwriting';
document.body.appendChild(promptMsg);


let ordStarList = starList.sort(function (x, y) { return x.t < y.t })

let planetRotFuncs = planetList.map(function (planet) {
	let planetRotate = new THREE.Matrix4().identity();
	planetRotate.multiply(new THREE.Matrix4().makeTranslation(planet.position.x, planet.position.y, planet.position.z));
	planetRotate.multiply(new THREE.Matrix4().makeRotationY(0.001));
	planetRotate.multiply(new THREE.Matrix4().makeTranslation(-planet.position.x, -planet.position.y, -planet.position.z));
	return _ => planet.applyMatrix4(planetRotate);
})

let planetRotate = new THREE.Matrix4().identity();
planetRotate.multiply(new THREE.Matrix4().makeTranslation(earthClouds.position.x, earthClouds.position.y, earthClouds.position.z));
planetRotate.multiply(new THREE.Matrix4().makeRotationZ(-0.001));
planetRotate.multiply(new THREE.Matrix4().makeTranslation(-earthClouds.position.x, -earthClouds.position.y, -earthClouds.position.z));

planetRotFuncs.push(_ => earthClouds.applyMatrix4(planetRotate))

function animate() {
	requestAnimationFrame(animate);
	planetRotFuncs.forEach(rotation => rotation())

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
	ordStarList = ordStarList.filter(x => x.tValue * NUM_POINTS > t && x.starObj.visible)
	ordStarList.forEach(function (star) {
		if (star.tValue * NUM_POINTS - t < COLLISION_EPSILON) {
			if (star.space == curveList[curveNum]) {
				if (star.isGood) collected += 1;
				else collected -= 3;
				star.starObj.visible = false;
			}
		}
	})
	score.innerHTML = "Score : " + collected;
	delta += clock.getDelta();

	if (delta > fps) {
		renderer.render(scene, camera);
		if (t < NUM_POINTS - 1) {
			clockTime += delta;
			time.innerHTML = "Time : " + clockTime.toPrecision(5);
		}
		delta = delta % fps;
	}

	if (t >= NUM_POINTS) {
		promptMsg.innerHTML = " Your Score is " + collected + " ";
	}


}
animate()