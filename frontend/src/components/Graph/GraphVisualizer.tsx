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
import * as dagre from 'dagre';

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

// Add layout configuration
const NODE_WIDTH = 250;
const NODE_HEIGHT = 80;
const LAYOUT_OPTIONS = {
  rankdir: 'LR', // Left to Right layout
  align: 'UL',
  nodesep: 80, // Horizontal spacing between nodes
  ranksep: 120, // Vertical spacing between ranks
  edgesep: 40, // Minimum separation between edges
};

// Layout helper function
function getLayoutedElements(nodes: Node[], edges: Edge[]) {
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));
  dagreGraph.setGraph(LAYOUT_OPTIONS);

  // Add nodes to dagre
  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: NODE_WIDTH, height: NODE_HEIGHT });
  });

  // Add edges to dagre
  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  // Calculate layout
  dagre.layout(dagreGraph);

  // Get positioned nodes
  const layoutedNodes = nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    return {
      ...node,
      position: {
        x: nodeWithPosition.x - NODE_WIDTH / 2,
        y: nodeWithPosition.y - NODE_HEIGHT / 2,
      },
    };
  });

  return { nodes: layoutedNodes, edges };
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
      case 'FLIGHT':
        return '✈️';
      case 'HOTEL':
        return '🏨';
      case 'CAR_RENTAL':
        return '🚗';
      case 'EXCURSION':
        return '🎯';
      default:
        return '🤖';
    }
  };

  const isActive = data.isCurrentNode;
  const isNext = data.isNextNode;

  return (
    <div 
      className={`px-4 py-2 shadow-lg rounded-lg border-2 transition-all duration-300
        ${isActive 
          ? 'bg-blue-50 border-blue-500 scale-110 shadow-blue-200' 
          : isNext
            ? 'bg-green-50 border-green-500 scale-105 shadow-green-200'
            : 'bg-white border-gray-200 hover:border-blue-300 hover:shadow-lg'
        }`}
    >
      <Handle 
        type="target" 
        position={Position.Left} 
        isConnectable={isConnectable}
        className={`!w-3 !h-3 !border-2 transition-colors
          ${isActive ? '!bg-blue-500 !border-blue-600' 
            : isNext ? '!bg-green-500 !border-green-600'
            : '!bg-gray-300 !border-gray-400'}`}
      />
      <div className="flex items-center gap-2">
        <div className={`p-2 rounded-lg ${
          isActive ? 'bg-blue-100' 
          : isNext ? 'bg-green-100'
          : 'bg-gray-100'}`}
        >
          <span className="text-2xl">{getNodeIcon(data.label)}</span>
        </div>
        <div className="flex flex-col">
          <span className={`font-medium ${
            isActive ? 'text-blue-700' 
            : isNext ? 'text-green-700'
            : 'text-gray-700'}`}
          >
            {data.label.replace(/_/g, ' ')}
          </span>
          {isActive && (
            <span className="text-xs text-blue-500">Active Agent</span>
          )}
          {isNext && (
            <span className="text-xs text-green-500">Next Agent</span>
          )}
        </div>
      </div>
      <Handle 
        type="source" 
        position={Position.Right} 
        isConnectable={isConnectable}
        className={`!w-3 !h-3 !border-2 transition-colors
          ${isActive ? '!bg-blue-500 !border-blue-600' 
            : isNext ? '!bg-green-500 !border-green-600'
            : '!bg-gray-300 !border-gray-400'}`}
      />
    </div>
  );
}

export default function GraphVisualizer({ graphState }: GraphVisualizerProps) {
  // Create initial nodes and edges
  const initialNodes: Node[] = useMemo(() => 
    graphState.nodes.map((node) => ({
      id: node,
      type: 'custom',
      position: { x: 0, y: 0 }, // Initial position will be updated by layout
      data: { 
        label: node,
        isCurrentNode: node === graphState.current_node,
        isNextNode: node === graphState.next_node
      }
    })), [graphState.nodes, graphState.current_node, graphState.next_node]);

  const initialEdges: Edge[] = useMemo(() => 
    graphState.edges.map(([source, target]) => ({
      id: `${source}-${target}`,
      source,
      target,
      type: 'smoothstep',
      animated: source === graphState.current_node && target === graphState.next_node,
      style: { 
        stroke: source === graphState.current_node && target === graphState.next_node
          ? '#22c55e' // green-500
          : '#94a3b8', // gray-400
        strokeWidth: source === graphState.current_node && target === graphState.next_node ? 3 : 2,
      }
    })), [graphState.edges, graphState.current_node, graphState.next_node]);

  // Apply layout
  const { nodes, edges } = useMemo(
    () => getLayoutedElements(initialNodes, initialEdges),
    [initialNodes, initialEdges]
  );

  const nodeTypes = useMemo(() => ({
    custom: CustomNode
  }), []);

  return (
    <div className="h-full w-full bg-white">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{ 
          padding: 0.2,
          minZoom: 0.5,
          maxZoom: 1.5
        }}
        className="bg-white"
        connectionMode={ConnectionMode.Loose}
        minZoom={0.5}
        maxZoom={1.5}
        defaultEdgeOptions={{
          style: { strokeWidth: 2 },
          animated: false,
          type: 'smoothstep'
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