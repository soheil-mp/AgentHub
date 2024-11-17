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

  return (
    <div className="px-4 py-2 shadow-lg rounded-lg border-2 bg-white min-w-[120px]">
      <Handle type="target" position={Position.Left} isConnectable={isConnectable} />
      <div className="flex items-center gap-2">
        <span className="text-xl">{getNodeIcon(data.label)}</span>
        <span className="font-medium">{data.label}</span>
      </div>
      <Handle type="source" position={Position.Right} isConnectable={isConnectable} />
    </div>
  );
}

export default function GraphVisualizer({ graphState }: GraphVisualizerProps) {
  const nodeTypes = useMemo(() => ({ custom: CustomNode }), []);

  const getNodeStyle = useCallback((nodeId: string) => {
    const isCurrent = nodeId === graphState.current_node;
    const isNext = nodeId === graphState.next_node;
    
    return {
      borderColor: isCurrent ? '#3b82f6' : isNext ? '#60a5fa' : '#64748b',
      borderWidth: isCurrent ? 2 : 1,
      background: isCurrent ? '#bfdbfe' : isNext ? '#dbeafe' : '#ffffff',
    };
  }, [graphState]);

  // Calculate node positions in a layered layout
  const nodes: Node[] = useMemo(() => {
    const columns = {
      ROUTER: 0,
      PRODUCT: 1,
      TECHNICAL: 1,
      CUSTOMER_SERVICE: 1,
      HUMAN: 2,
    };

    const rows = {
      ROUTER: 1,
      PRODUCT: 0,
      TECHNICAL: 1,
      CUSTOMER_SERVICE: 2,
      HUMAN: 1,
    };

    return graphState.nodes.map((nodeId) => ({
      id: nodeId,
      type: 'custom',
      data: { label: nodeId },
      position: {
        x: columns[nodeId as keyof typeof columns] * 250 + 50,
        y: rows[nodeId as keyof typeof rows] * 150 + 50,
      },
      style: getNodeStyle(nodeId),
    }));
  }, [graphState.nodes, getNodeStyle]);

  const edges: Edge[] = useMemo(() => 
    graphState.edges.map(([source, target], index) => ({
      id: `${source}-${target}`,
      source,
      target,
      animated: source === graphState.current_node && target === graphState.next_node,
      style: {
        stroke: source === graphState.current_node && target === graphState.next_node
          ? '#3b82f6'
          : '#64748b',
        strokeWidth: source === graphState.current_node && target === graphState.next_node
          ? 2
          : 1,
      },
      type: 'smoothstep',
      markerEnd: {
        type: 'arrowclosed',
        color: source === graphState.current_node && target === graphState.next_node
          ? '#3b82f6'
          : '#64748b',
      },
    })), [graphState]);

  return (
    <div style={{ height: 400 }} className="bg-white rounded-lg shadow-sm">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        connectionMode={ConnectionMode.Loose}
        fitView
        minZoom={0.5}
        maxZoom={1.5}
        defaultViewport={{ x: 0, y: 0, zoom: 1 }}
      >
        <Background />
        <Controls />
        <Panel position="top-left" className="bg-white p-2 rounded shadow-sm">
          <div className="text-sm font-medium">Agent Status</div>
          <div className="text-xs text-gray-600">
            Current: {graphState.current_node} {' '}
            {graphState.next_node && `→ Next: ${graphState.next_node}`}
          </div>
        </Panel>
      </ReactFlow>
    </div>
  );
} 