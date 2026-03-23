import { useState } from "react";

export default function FactoryTwin({ machines }) {

  const [selectedMachine, setSelectedMachine] = useState(null);

  if (!machines || Object.keys(machines).length === 0) {
    return <div>Loading Digital Twin...</div>;
  }

  const getColor = (health) => {

    if (health === "healthy") return "#22c55e";
    if (health === "warning") return "#f59e0b";
    if (health === "critical") return "#ef4444";

    return "#6b7280";
  };

  const machineList = Object.values(machines);

  return (

    <div style={{
      background:"#0f172a",
      padding:"30px",
      borderRadius:"12px",
      marginTop:"20px"
    }}>

      <h2 style={{marginBottom:"20px"}}>🏭 Factory Digital Twin</h2>

      {/* PRODUCTION LINE */}
      <div style={{
        display:"flex",
        alignItems:"center",
        justifyContent:"center",
        gap:"0px"
      }}>

        {machineList.map((machine, index) => (

          <div key={machine.machine_id} style={{display:"flex",alignItems:"center"}}>

            {/* MACHINE */}
            <div
              onClick={() => setSelectedMachine(machine)}
              style={{
                width:"80px",
                height:"80px",
                borderRadius:"10px",
                background:getColor(machine.health_status),
                display:"flex",
                alignItems:"center",
                justifyContent:"center",
                fontWeight:"bold",
                cursor:"pointer"
              }}
            >
              {machine.machine_id}
            </div>

            {/* CONVEYOR */}
            {index < machineList.length - 1 && (

              <div style={{
                width:"120px",
                height:"12px",
                background:"#334155",
                position:"relative",
                overflow:"hidden"
              }}>

                {/* MOVING BELT */}
                <div style={{
                  width:"40px",
                  height:"12px",
                  background:"#64748b",
                  position:"absolute",
                  animation:"beltMove 2s linear infinite"
                }}/>

              </div>

            )}

          </div>

        ))}

      </div>

      {/* MACHINE INFO PANEL */}
      {selectedMachine && (

        <div style={{
          marginTop:"20px",
          padding:"20px",
          background:"#020617",
          borderRadius:"10px"
        }}>

          <h3>{selectedMachine.machine_id} Details</h3>

          <p>Temperature: {selectedMachine.temperature} °C</p>
          <p>Torque: {selectedMachine.torque}</p>
          <p>Vibration: {selectedMachine.vibration_index}</p>
          <p>Failure Risk: {selectedMachine.prediction?.failure_probability}%</p>

        </div>

      )}

      {/* BELT ANIMATION */}
      <style>
        {`
        @keyframes beltMove {
          from { left:-40px }
          to { left:120px }
        }
        `}
      </style>

    </div>
  );

}