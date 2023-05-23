import { ShapeProps } from '../interfaces';

interface EnumMember {
  value: number;
  description: string;
}

interface EnumType {
  [key: string]: EnumMember;
}

function createEnumMember(value: number, description: string): EnumMember {
  return { value, description };
}

function getIndex(enumObj: EnumType, value: number): number {
  const keys = Object.keys(enumObj) as Array<keyof typeof enumObj>;
  for (let i = 0; i < keys.length; i++) {
    if (enumObj[keys[i]].value === value) {
      return i;
    }
  }
  throw new Error(`Invalid value ${value}`);
}

enum Type1Shape1Q {
  NONE = 0,
  SOLID = 1,
  DOTTED = 2,
  CATSEYE = 3,
  ZIGZAG = 4
}

const Type1Shape1QEnum: EnumType = {
  NONE: createEnumMember(Type1Shape1Q.NONE, 'None'),
  SOLID: createEnumMember(Type1Shape1Q.SOLID, 'Solid'),
  DOTTED: createEnumMember(Type1Shape1Q.DOTTED, 'Dotted'),
  CATSEYE: createEnumMember(Type1Shape1Q.CATSEYE, 'CatsEye'),
  ZIGZAG: createEnumMember(Type1Shape1Q.ZIGZAG, 'Zigzag'),
};

enum Type2SingleDoubleW {
  NONE = 0,
  SINGLE = 1,
  DOUBLE = 2,
  ACCESSORIES = 3,
}

const Type2SingleDoubleWEnum: EnumType = {
  NONE: createEnumMember(Type2SingleDoubleW.NONE, 'None'),
  SINGLE: createEnumMember(Type2SingleDoubleW.SINGLE, 'Single'),
  DOUBLE: createEnumMember(Type2SingleDoubleW.DOUBLE, 'Double'),
  ACCESSORIES: createEnumMember(Type2SingleDoubleW.ACCESSORIES, 'Accessories'),
};

enum Type3PositionE {
  NONE = 0,
  L = -255,
  L1 = 1,
  L1_2 = 1537,
  L2 = 257,
  L3 = 513,
  L4 = 769,
  L5 = 1025,
  L6 = 1281,
  LU = 1793,

  R = -254,
  R1 = 2,
  R1_2 = 1538,
  R2 = 258,
  R3 = 514,
  R4 = 770,
  R5 = 1026,
  R6 = 1282,
  RU = 1794,

  U = -253
}

const Type3PositionEEnum: EnumType = {
  NONE: createEnumMember(Type3PositionE.NONE, 'None'),
  L: createEnumMember(Type3PositionE.L, 'L'),
  L1: createEnumMember(Type3PositionE.L1, 'L1'),
  L1_2: createEnumMember(Type3PositionE.L1_2, 'L1_2'),
  L2: createEnumMember(Type3PositionE.L2, 'L2'),
  L3: createEnumMember(Type3PositionE.L3, 'L3'),
  L4: createEnumMember(Type3PositionE.L4, 'L4'),
  L5: createEnumMember(Type3PositionE.L5, 'L5'),
  L6: createEnumMember(Type3PositionE.L6, 'L6'),
  LU: createEnumMember(Type3PositionE.LU, 'U(LU)'),

  R: createEnumMember(Type3PositionE.R, 'R'),
  R1: createEnumMember(Type3PositionE.R1, 'R1'),
  R1_2: createEnumMember(Type3PositionE.R1_2, 'R1_2'),
  R2: createEnumMember(Type3PositionE.R2, 'R2'),
  R3: createEnumMember(Type3PositionE.R3, 'R3'),
  R4: createEnumMember(Type3PositionE.R4, 'R4'),
  R5: createEnumMember(Type3PositionE.R5, 'R5'),
  R6: createEnumMember(Type3PositionE.R6, 'R6'),
  RU: createEnumMember(Type3PositionE.RU, 'U(RU)'),

  U: createEnumMember(Type3PositionE.U, 'U'),
};

enum Type4UnusualCaseR {
  NONE = 0,
  COMBINATION = 1,
  BRANCH = 2,
  UNUSED = 3,
  OPPOSITE = 4
}

const Type4UnusualCaseREnum: EnumType = {
  NONE: createEnumMember(Type4UnusualCaseR.NONE, 'None'),
  COMBINATION: createEnumMember(Type4UnusualCaseR.COMBINATION, 'Combination'),
  BRANCH: createEnumMember(Type4UnusualCaseR.BRANCH, 'Branch'),
  UNUSED: createEnumMember(Type4UnusualCaseR.UNUSED, 'Unused'),
  OPPOSITE: createEnumMember(Type4UnusualCaseR.OPPOSITE, 'Opposite')
};

enum BoundaryType2R {
  NONE = 0,
  BEACON = 9,
  PLASTIC_WALL = 7,
  DRUM = 8,
  CONE = 10,
  WALL = 1,
  GUARDRAIL = 3,
  FIXED_DIVIDER = 4,
  TEMPORARY_DIVIDER = 6,
  FIXED_PARKING = 2,
  STRUCTURE = 14,
  CURB = 5,
  EDGE = 11,
  INDOOR_PARKING_LOT = 12,
  UNEXPLAINABLE = 13,
  ETC = 15,
  LOW_CURB = 16,
  LOW_BOUNDARY = 17,
  SNOW_PILE = 18,
  SNOW_WALL = 19
}

const BoundaryType2REnum: EnumType = {
  NONE: createEnumMember(BoundaryType2R.NONE, 'None'),
  BEACON: createEnumMember(BoundaryType2R.BEACON, 'Beacon(1)'),
  PLASTIC_WALL: createEnumMember(BoundaryType2R.PLASTIC_WALL, 'Plastic wall(2)'),
  DRUM: createEnumMember(BoundaryType2R.DRUM, 'Drum(3)'),
  CONE: createEnumMember(BoundaryType2R.CONE, 'Cone(4)'),
  WALL: createEnumMember(BoundaryType2R.WALL, 'Wall(5)'),
  GUARDRAIL: createEnumMember(BoundaryType2R.GUARDRAIL, 'Guardrail(6)'),
  FIXED_DIVIDER: createEnumMember(BoundaryType2R.FIXED_DIVIDER, 'Fixed divider(7)'),
  TEMPORARY_DIVIDER: createEnumMember(BoundaryType2R.TEMPORARY_DIVIDER, 'Temporary divider(8)'),
  FIXED_PARKING: createEnumMember(BoundaryType2R.FIXED_PARKING, 'Fixed parking(9)'),
  STRUCTURE: createEnumMember(BoundaryType2R.STRUCTURE, 'Structure(10)'),
  CURB: createEnumMember(BoundaryType2R.CURB, 'Curb(11)'),
  EDGE: createEnumMember(BoundaryType2R.EDGE, 'Edge(12)'),
  INDOOR_PARKING_LOT: createEnumMember(BoundaryType2R.INDOOR_PARKING_LOT, 'Indoor parking lot(12)'),
  UNEXPLAINABLE: createEnumMember(BoundaryType2R.UNEXPLAINABLE, 'Unexplainable(14)'),
  ETC: createEnumMember(BoundaryType2R.ETC, 'Etc.(15)'),
  LOW_CURB: createEnumMember(BoundaryType2R.LOW_CURB, 'Low curb(16)'),
  LOW_BOUNDARY: createEnumMember(BoundaryType2R.LOW_BOUNDARY, 'Low boundary(17)'),
  SNOW_PILE: createEnumMember(BoundaryType2R.SNOW_PILE, 'Snow pile(18)'),
  SNOW_WALL: createEnumMember(BoundaryType2R.SNOW_WALL, 'Snow wall(19)')
}

enum Type5ColorS {
  NONE = 0,
  WHITE = 1,
  YELLOW = 2,
  BLUE = 3,
  OTHER = 4,
}

const Type5ColorSEnum: EnumType = {
  NONE: createEnumMember(Type5ColorS.NONE, 'None'),
  WHITE: createEnumMember(Type5ColorS.WHITE, 'White'),
  YELLOW: createEnumMember(Type5ColorS.YELLOW, 'Yellow'),
  BLUE: createEnumMember(Type5ColorS.BLUE, 'Blue'),
  OTHER: createEnumMember(Type5ColorS.OTHER, 'Other'),
};

enum Type6BicycleD {
  NONE = 0,
  BICYCLED = 1,
}

const Type6BicycleDEnum: EnumType = {
  NONE: createEnumMember(Type6BicycleD.NONE, 'None'),
  BICYCLED: createEnumMember(Type6BicycleD.BICYCLED, 'Bicycle'),
};

enum TypeRoadMarkerQ {
  NONE = 0,
  STOP_LINE = 1,
  PEDESTRIAN_CROSSING = 2,
  DIRECTIONAL_ARROWS = 3,
  SPEED_BREAKER = 4
}

const TypeRoadMarkerQEnum: EnumType = {
  NONE: createEnumMember(TypeRoadMarkerQ.NONE, 'Uncertain/difficult to classify'),
  STOP_LINE: createEnumMember(TypeRoadMarkerQ.STOP_LINE, 'Stop line'),
  DIRECTIONAL_ARROWS: createEnumMember(TypeRoadMarkerQ.DIRECTIONAL_ARROWS, 'Directional arrows'),
  SPEED_BREAKER: createEnumMember(TypeRoadMarkerQ.SPEED_BREAKER, 'Speed bump/Speed breaker')
};

interface PropertyMappings {
  [property: string]: {
    enumObj: EnumType;
    keyName: string;
  };
}


function fromAttributes(json: any, propertyMappings: PropertyMappings): any {
  const convertedJson: any = {};

  for (const property in propertyMappings) {
    if (json.hasOwnProperty(property)) {
      const { enumObj, keyName } = propertyMappings[property];
      const value = Number(json[property]);
      const index = getIndex(enumObj, value);
      const enumKey = Object.keys(enumObj)[index];
      convertedJson[keyName] = enumObj[enumKey].description;
    }
  }

  return JSON.stringify(convertedJson, null, 2);

}

function fromSplineAttributes(json: any): any {
  const propertyMappings: PropertyMappings = {
    'type1': {
      enumObj: Type1Shape1QEnum,
      keyName: '1.Shape1(Q)',
    },
    'type2': {
      enumObj: Type2SingleDoubleWEnum,
      keyName: '2.Single/Double(W)',
    },
    'type3': {
      enumObj: Type3PositionEEnum,
      keyName: '3.Position(E)',
    },
    'type4': {
      enumObj: Type4UnusualCaseREnum,
      keyName: '4.Unusual Case(R)',
    },
    'type5': {
      enumObj: Type5ColorSEnum,
      keyName: '5.Color(S)',
    },
    'type6': {
      enumObj: Type6BicycleDEnum,
      keyName: '6.Bicycle(S)',
    },
  };

  return fromAttributes(json, propertyMappings);
}

function fromBoundaryAttributes(json: any): any {
  const propertyMappings: PropertyMappings = {
    'type3': {
      enumObj: Type3PositionEEnum,
      keyName: '3.Position(E)',
    },
    'boundary': {
      enumObj: BoundaryType2REnum,
      keyName: '2.Boundary type(R)',
    },
  };

  return fromAttributes(json, propertyMappings);
}

function fromPolygonAttributes(json: any): any {
  const propertyMappings: PropertyMappings = {
    'type': {
      enumObj: TypeRoadMarkerQEnum,
      keyName: '1.Road marker type(Q)',
    }
  };

  return fromAttributes(json, propertyMappings);
}

export function displayAttributes(shape: ShapeProps): any {
  let convertedJson: any = {};
  const attributes = shape.attributes;

  if (shape.shapeType === 'spline') {
    convertedJson = fromSplineAttributes(attributes);

  } else if (shape.shapeType === 'boundary') {
    convertedJson = fromBoundaryAttributes(attributes);
  } else if (shape.shapeType === 'polygon') {
    convertedJson = fromPolygonAttributes(attributes);
  } else {
    convertedJson = attributes;
  }

  return convertedJson;
}