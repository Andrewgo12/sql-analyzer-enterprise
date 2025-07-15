import React, { useState, useEffect, useRef } from 'react';
import {
  Terminal,
  Play,
  Square,
  Trash2,
  Download,
  Upload,
  Settings,
  Maximize2,
  Minimize2,
  Copy,
  Save,
  RefreshCw,
  HelpCircle,
  Clock,
  User,
  Server,
  Zap
} from 'lucide-react';

const TerminalView = ({
  terminalOutput,
  setTerminalOutput,
  terminalInput,
  setTerminalInput,
  onExecuteCommand,
  systemMetrics,
  connections,
  onAnalyze
}) => {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [terminalSettings, setTerminalSettings] = useState({
    fontSize: 14,
    theme: 'dark',
    showTimestamps: true,
    autoScroll: true,
    maxLines: 1000
  });
  const [commandHistory, setCommandHistory] = useState([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [isProcessing, setIsProcessing] = useState(false);
  const terminalRef = useRef(null);
  const inputRef = useRef(null);

  const availableCommands = [
    { cmd: 'help', desc: 'Mostrar ayuda de comandos disponibles' },
    { cmd: 'clear', desc: 'Limpiar la pantalla del terminal' },
    { cmd: 'status', desc: 'Mostrar estado del sistema' },
    { cmd: 'analyze', desc: 'Ejecutar análisis SQL del editor actual' },
    { cmd: 'connections', desc: 'Listar conexiones de base de datos' },
    { cmd: 'history', desc: 'Mostrar historial de comandos' },
    { cmd: 'metrics', desc: 'Mostrar métricas del sistema en tiempo real' },
    { cmd: 'version', desc: 'Mostrar información de versión' },
    { cmd: 'export', desc: 'Exportar logs del terminal' },
    { cmd: 'ping', desc: 'Probar conectividad de red' },
    { cmd: 'ps', desc: 'Mostrar procesos activos' },
    { cmd: 'uptime', desc: 'Mostrar tiempo de actividad del sistema' },
    { cmd: 'whoami', desc: 'Mostrar información del usuario actual' },
    { cmd: 'date', desc: 'Mostrar fecha y hora actual' },
    { cmd: 'echo', desc: 'Mostrar texto en pantalla' }
  ];

  useEffect(() => {
    if (terminalSettings.autoScroll && terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [terminalOutput, terminalSettings.autoScroll]);

  useEffect(() => {
    // Limit terminal output lines
    if (terminalOutput.length > terminalSettings.maxLines) {
      setTerminalOutput(prev => prev.slice(-terminalSettings.maxLines));
    }
  }, [terminalOutput, terminalSettings.maxLines, setTerminalOutput]);

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && terminalInput.trim()) {
      executeCommand(terminalInput.trim());
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (historyIndex < commandHistory.length - 1) {
        const newIndex = historyIndex + 1;
        setHistoryIndex(newIndex);
        setTerminalInput(commandHistory[commandHistory.length - 1 - newIndex]);
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (historyIndex > 0) {
        const newIndex = historyIndex - 1;
        setHistoryIndex(newIndex);
        setTerminalInput(commandHistory[commandHistory.length - 1 - newIndex]);
      } else if (historyIndex === 0) {
        setHistoryIndex(-1);
        setTerminalInput('');
      }
    } else if (e.key === 'Tab') {
      e.preventDefault();
      handleAutoComplete();
    }
  };

  const handleAutoComplete = () => {
    const matches = availableCommands.filter(cmd => 
      cmd.cmd.startsWith(terminalInput.toLowerCase())
    );
    
    if (matches.length === 1) {
      setTerminalInput(matches[0].cmd);
    } else if (matches.length > 1) {
      addOutput('system', `Comandos disponibles: ${matches.map(m => m.cmd).join(', ')}`);
    }
  };

  const executeCommand = async (command) => {
    setIsProcessing(true);
    
    // Add command to history
    setCommandHistory(prev => [...prev, command]);
    setHistoryIndex(-1);
    
    // Add command to output
    addOutput('command', `$ ${command}`);
    
    // Process command
    const [cmd, ...args] = command.split(' ');
    const result = await processCommand(cmd.toLowerCase(), args);
    
    // Add result to output
    if (result) {
      addOutput('result', result);
    }
    
    setTerminalInput('');
    setIsProcessing(false);
  };

  const addOutput = (type, content) => {
    const newOutput = {
      id: Date.now() + Math.random(),
      timestamp: new Date().toLocaleTimeString(),
      type,
      content
    };
    setTerminalOutput(prev => [...prev, newOutput]);
  };

  const processCommand = async (cmd, args) => {
    switch (cmd) {
      case 'help':
        return availableCommands
          .map(c => `  ${c.cmd.padEnd(12)} - ${c.desc}`)
          .join('\n');
      
      case 'clear':
        setTerminalOutput([]);
        return null;
      
      case 'status':
        return `Sistema: SQL Analyzer Enterprise v2.0.0
Estado: Operativo
CPU: ${systemMetrics.cpu}%
Memoria: ${systemMetrics.memory}%
Disco: ${systemMetrics.disk}%
Red: ${systemMetrics.network}%
Conexiones: ${connections.length} configuradas`;
      
      case 'analyze':
        if (onAnalyze) {
          onAnalyze();
          return 'Iniciando análisis SQL...';
        }
        return 'Error: No hay contenido SQL para analizar';
      
      case 'connections':
        if (connections.length === 0) {
          return 'No hay conexiones configuradas';
        }
        return connections
          .map(c => `  ${c.name} (${c.engine}) - ${c.status || 'inactive'}`)
          .join('\n');
      
      case 'history':
        if (commandHistory.length === 0) {
          return 'No hay comandos en el historial';
        }
        return commandHistory
          .slice(-10)
          .map((cmd, i) => `  ${i + 1}. ${cmd}`)
          .join('\n');
      
      case 'metrics':
        return `Métricas del Sistema:
┌─────────────┬─────────┬────────────┐
│ Componente  │ Uso     │ Estado     │
├─────────────┼─────────┼────────────┤
│ CPU         │ ${systemMetrics.cpu.toString().padEnd(6)}% │ ${systemMetrics.cpu < 70 ? 'Normal' : systemMetrics.cpu < 85 ? 'Alto' : 'Crítico'} │
│ Memoria     │ ${systemMetrics.memory.toString().padEnd(6)}% │ ${systemMetrics.memory < 70 ? 'Normal' : systemMetrics.memory < 85 ? 'Alto' : 'Crítico'} │
│ Disco       │ ${systemMetrics.disk.toString().padEnd(6)}% │ ${systemMetrics.disk < 70 ? 'Normal' : systemMetrics.disk < 85 ? 'Alto' : 'Crítico'} │
│ Red         │ ${systemMetrics.network.toString().padEnd(6)}% │ Normal     │
└─────────────┴─────────┴────────────┘`;
      
      case 'version':
        return `SQL Analyzer Enterprise v2.0.0
Build: 2024.07.15
Node.js: ${navigator.userAgent}
Platform: ${navigator.platform}`;
      
      case 'export':
        const exportData = terminalOutput
          .map(line => `[${line.timestamp}] ${line.type}: ${line.content}`)
          .join('\n');
        
        const blob = new Blob([exportData], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `terminal-log-${new Date().toISOString().split('T')[0]}.txt`;
        a.click();
        URL.revokeObjectURL(url);
        
        return 'Log del terminal exportado exitosamente';
      
      case 'ping':
        const target = args[0] || 'localhost';
        return `PING ${target}: 64 bytes from ${target}: icmp_seq=1 ttl=64 time=0.5ms`;
      
      case 'ps':
        return `PID    COMMAND
1234   sql-analyzer-backend
5678   sql-analyzer-frontend
9012   terminal-service`;
      
      case 'uptime':
        const uptime = Math.floor(Math.random() * 24);
        return `Sistema activo por ${uptime} horas, 3 usuarios conectados`;
      
      case 'whoami':
        return 'sql-analyzer-user';
      
      case 'date':
        return new Date().toString();
      
      case 'echo':
        return args.join(' ');
      
      default:
        return `Comando no reconocido: ${cmd}. Escribe 'help' para ver comandos disponibles.`;
    }
  };

  const handleCopyOutput = () => {
    const outputText = terminalOutput
      .map(line => `[${line.timestamp}] ${line.content}`)
      .join('\n');
    
    navigator.clipboard.writeText(outputText);
    addOutput('system', 'Contenido del terminal copiado al portapapeles');
  };

  const renderTerminalLine = (line) => (
    <div key={line.id} className={`terminal-line ${line.type}`}>
      {terminalSettings.showTimestamps && (
        <span className="terminal-timestamp">[{line.timestamp}]</span>
      )}
      <span className="terminal-content">{line.content}</span>
    </div>
  );

  const renderSettings = () => (
    <div className="terminal-settings">
      <h3>Configuración del Terminal</h3>
      
      <div className="settings-group">
        <label>Tamaño de fuente</label>
        <input
          type="range"
          min="10"
          max="20"
          value={terminalSettings.fontSize}
          onChange={(e) => setTerminalSettings(prev => ({ 
            ...prev, 
            fontSize: parseInt(e.target.value) 
          }))}
        />
        <span>{terminalSettings.fontSize}px</span>
      </div>
      
      <div className="settings-group">
        <label>Máximo de líneas</label>
        <input
          type="number"
          min="100"
          max="5000"
          value={terminalSettings.maxLines}
          onChange={(e) => setTerminalSettings(prev => ({ 
            ...prev, 
            maxLines: parseInt(e.target.value) 
          }))}
        />
      </div>
      
      <div className="settings-group">
        <label>
          <input
            type="checkbox"
            checked={terminalSettings.showTimestamps}
            onChange={(e) => setTerminalSettings(prev => ({ 
              ...prev, 
              showTimestamps: e.target.checked 
            }))}
          />
          Mostrar marcas de tiempo
        </label>
      </div>
      
      <div className="settings-group">
        <label>
          <input
            type="checkbox"
            checked={terminalSettings.autoScroll}
            onChange={(e) => setTerminalSettings(prev => ({ 
              ...prev, 
              autoScroll: e.target.checked 
            }))}
          />
          Desplazamiento automático
        </label>
      </div>
    </div>
  );

  return (
    <div className="terminal-view">
      <div className="view-header">
        <div className="header-title">
          <Terminal size={24} />
          <h1>Terminal Integrado</h1>
        </div>
        <div className="header-actions">
          <button 
            className="btn-secondary"
            onClick={() => setTerminalOutput([])}
          >
            <Trash2 size={16} />
            Limpiar
          </button>
          <button 
            className="btn-secondary"
            onClick={handleCopyOutput}
          >
            <Copy size={16} />
            Copiar
          </button>
          <button 
            className="btn-secondary"
            onClick={() => setIsFullscreen(!isFullscreen)}
          >
            {isFullscreen ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
            {isFullscreen ? 'Minimizar' : 'Pantalla completa'}
          </button>
        </div>
      </div>

      <div className={`terminal-container ${isFullscreen ? 'fullscreen' : ''}`}>
        <div className="terminal-header">
          <div className="terminal-title">
            <Server size={16} />
            <span>SQL Analyzer Enterprise Terminal</span>
          </div>
          <div className="terminal-status">
            <div className={`status-indicator ${isProcessing ? 'processing' : 'ready'}`}></div>
            <span>{isProcessing ? 'Procesando...' : 'Listo'}</span>
          </div>
        </div>

        <div 
          ref={terminalRef}
          className="terminal-output"
          style={{ fontSize: `${terminalSettings.fontSize}px` }}
        >
          {terminalOutput.map(renderTerminalLine)}
          {isProcessing && (
            <div className="terminal-line processing">
              <RefreshCw size={14} className="spinning" />
              <span>Procesando comando...</span>
            </div>
          )}
        </div>

        <div className="terminal-input-container">
          <div className="terminal-prompt">
            <User size={14} />
            <span>sql-analyzer@enterprise:~$</span>
          </div>
          <input
            ref={inputRef}
            type="text"
            value={terminalInput}
            onChange={(e) => setTerminalInput(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Escribe un comando... (Tab para autocompletar)"
            className="terminal-input"
            style={{ fontSize: `${terminalSettings.fontSize}px` }}
            disabled={isProcessing}
            autoFocus
          />
        </div>
      </div>

      <div className="terminal-help">
        <div className="help-section">
          <h3>
            <HelpCircle size={16} />
            Comandos Disponibles
          </h3>
          <div className="commands-grid">
            {availableCommands.slice(0, 8).map((cmd, index) => (
              <div key={index} className="command-item">
                <code>{cmd.cmd}</code>
                <span>{cmd.desc}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="help-section">
          <h3>
            <Zap size={16} />
            Atajos de Teclado
          </h3>
          <div className="shortcuts-grid">
            <div className="shortcut-item">
              <kbd>↑/↓</kbd>
              <span>Navegar historial de comandos</span>
            </div>
            <div className="shortcut-item">
              <kbd>Tab</kbd>
              <span>Autocompletar comando</span>
            </div>
            <div className="shortcut-item">
              <kbd>Ctrl+C</kbd>
              <span>Copiar salida del terminal</span>
            </div>
            <div className="shortcut-item">
              <kbd>Ctrl+L</kbd>
              <span>Limpiar terminal</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TerminalView;
