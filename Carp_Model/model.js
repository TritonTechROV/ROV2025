let regions = [];
let map;
const graph = [
  // R1   R2   R3   R4   R5
   ['N', 'N', 'N', 'N', 'N'], // 2016
   ['Y', 'N', 'N', 'N', 'N'], // 2017
   ['Y', 'N', 'N', 'N', 'N'], // 2018
   ['Y', 'N', 'N', 'N', 'N'], // 2019
   ['Y', 'Y', 'Y', 'N', 'N'], // 2020
   ['Y', 'Y', 'Y', 'N', 'N'], // 2021
   ['Y', 'Y', 'Y', 'N', 'N'], // 2022
   ['Y', 'Y', 'Y', 'Y', 'N'], // 2023
   ['Y', 'Y', 'Y', 'Y', 'N'], // 2024
   ['Y', 'Y', 'Y', 'Y', 'Y'], // 2025
];

const years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025];
let yearIndex= 0;


function preload() {
    
    map = loadImage ('images/map.png')

    for (let i = 1; i <= 5; i++) {
    regions.push(loadImage(`images/region${i}.png`));
}

}
function setup() {
    createCanvas(1900,899);
    imageMode(CENTER);
}



function draw() {
  background(255);
  image(map, width / 2, height / 2, 700, 899);



  for (let i = 0; i <= regions.length; i++) {
    if (graph[yearIndex][i] === 'Y') {
      image(regions[i], width / 2, height / 2, 700, 899 );
    }
  }

  fill('#FF0000');
  textSize(75);
  textAlign(CENTER);
  text(years[yearIndex], 1250, 500);
}

function keyPressed() {
  if (keyCode === RIGHT_ARROW) {
    if (yearIndex < years.length - 1) {
      yearIndex++;
    }
}

    if (keyCode === LEFT_ARROW) {
        if (yearIndex > 0) {
            yearIndex--;
        }
    }

    if (key === ' ') {
    yearIndex = 0;
    }
}
