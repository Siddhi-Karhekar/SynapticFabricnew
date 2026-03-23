import React, { useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";

function getMachineColor(machine) {

  if (!machine) return "#888";

  if (machine.health_status === "Critical") return "#ff3b3b";
  if (machine.health_status === "Warning") return "#ffa500";
  if (machine.health_status === "Healthy") return "#00ff88";

  return "#888";
}

function ConveyorBox({ start }) {

  const ref = useRef();

  useFrame(() => {

    ref.current.position.x += 0.05;

    if (ref.current.position.x > 12)
      ref.current.position.x = -12;

  });

  return (
    <mesh ref={ref} position={[start,0.5,0]}>
      <boxGeometry args={[0.6,0.6,0.6]}/>
      <meshStandardMaterial color="#cccccc"/>
    </mesh>
  );
}

function Machine({ machine, position }) {

  const color = getMachineColor(machine);

  return (
    <mesh position={position}>
      <boxGeometry args={[2,2,2]}/>
      <meshStandardMaterial
        color={color}
        emissive={color}
        emissiveIntensity={0.5}
      />
    </mesh>
  );
}

export default function FactoryTwin3D({ machines }) {

  const machineArray = Object.values(machines || {});

  return (

    <div style={{height:"300px",width:"100%"}}>

      <Canvas camera={{position:[0,8,14],fov:60}}>

        <ambientLight intensity={0.6}/>
        <directionalLight position={[10,10,5]}/>

        {/* floor */}
        <mesh rotation={[-Math.PI/2,0,0]} position={[0,-1,0]}>
          <planeGeometry args={[40,20]}/>
          <meshStandardMaterial color="#222"/>
        </mesh>

        {/* conveyor belt */}
        <mesh position={[0,0,0]}>
          <boxGeometry args={[30,0.5,2]}/>
          <meshStandardMaterial color="#111"/>
        </mesh>

        {/* moving boxes */}
        <ConveyorBox start={-10}/>
        <ConveyorBox start={-3}/>
        <ConveyorBox start={4}/>

        {/* machines */}
        {machineArray.map((machine,i)=>{

          const spacing=8;
          const start=-(machineArray.length-1)*spacing/2;

          return (
            <Machine
              key={machine.machine_id}
              machine={machine}
              position={[start+i*spacing,1,0]}
            />
          )

        })}

        <OrbitControls/>

      </Canvas>

    </div>

  );
}