import React, { useCallback, useMemo } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Background,
  Controls,
  ConnectionMode,
  Panel,
  NodeProps,
  Handle,
  Position,
} from 'reactflow';
import 'reactflow/dist/style.css';

interface GraphState {
  current_node: string;
  next_node: string;
  nodes: string[];
  edges: [string, string][];
  requires_action: boolean;
}

interface GraphVisualizerProps {
  graphState: GraphState;
}

// Custom node component with icon and better styling
function CustomNode({ data, isConnectable }: NodeProps) {
  const getNodeIcon = (nodeId: string) => {
    switch (nodeId) {
      case 'ROUTER':
        return '🔄';
      case 'PRODUCT':
        return '📦';
      case 'TECHNICAL':
        return '🔧';
      case 'CUSTOMER_SERVICE':
        return '👥';
      case 'HUMAN':
        return '🤝';
      default:
        return '🤖';
    }
  };

  const isActive = data.isCurrentNode;

  return (
    <div 
      className={`px-4 py-2 shadow-lg rounded-lg border-2 transition-all duration-300
        ${isActive 
          ? 'bg-blue-50 border-blue-500 scale-110 shadow-blue-100' 
          : 'bg-white border-gray-200 hover:border-blue-300 hover:shadow-lg'
        }`}
    >
      <Handle 
        type="target" 
        position={Position.Left} 
        isConnectable={isConnectable}
        className="!bg-gray-400 !w-3 !h-3"
      />
      <div className="flex items-center gap-2">
        <div className={`p-1 rounded ${isActive ? 'bg-blue-100' : 'bg-gray-100'}`}>
          <span className="text-xl">{getNodeIcon(data.label)}</span>
        </div>
        <div className="flex flex-col">
          <span className={`font-medium ${isActive ? 'text-blue-700' : 'text-gray-700'}`}>
            {data.label}
          </span>
          {isActive && (
            <span className="text-xs text-blue-500">Active Agent</span>
          )}
        </div>
      </div>
      <Handle 
        type="source" 
        position={Position.Right} 
        isConnectable={isConnectable}
        className="!bg-gray-400 !w-3 !h-3"
      />
    </div>
  );
}

export default function GraphVisualizer({ graphState }: GraphVisualizerProps) {
  const nodes: Node[] = useMemo(() => 
    graphState.nodes.map((node) => ({
      id: node,
      type: 'custom',
      position: { x: 0, y: 0 }, // Positions will be calculated by layout
      data: { 
        label: node,
        isCurrentNode: node === graphState.current_node 
      }
    })), [graphState.nodes, graphState.current_node]);

  const edges: Edge[] = useMemo(() => 
    graphState.edges.map(([source, target], index) => ({
      id: `${source}-${target}`,
      source,
      target,
      type: 'smoothstep',
      animated: source === graphState.current_node && target === graphState.next_node,
      style: { stroke: '#94a3b8' }
    })), [graphState.edges, graphState.current_node, graphState.next_node]);

  const nodeTypes = useMemo(() => ({
    custom: CustomNode
  }), []);

  return (
    <div className="h-full w-full bg-gray-50/50">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        fitView
        className="bg-gray-50/50"
        connectionMode={ConnectionMode.Loose}
        minZoom={0.5}
        maxZoom={1.5}
        defaultEdgeOptions={{
          style: { strokeWidth: 2 },
          animated: true
        }}
      >
        <Background color="#94a3b8" gap={16} />
        <Controls 
          className="bg-white border border-gray-200 shadow-sm"
          showInteractive={false}
        />
      </ReactFlow>
    </div>
  );
} 