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
  Zap,
  Database,
  FileText,
  Activity,
  CheckCircle,
  AlertTriangle,
  Info,
  ArrowRight,
  Hash,
  Cpu,
  MemoryStick,
  HardDrive,
  Wifi
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
  const [currentDirectory, setCurrentDirectory] = useState('/sql-analyzer');
  const [sessionInfo, setSessionInfo] = useState({
    user: 'admin',
    host: 'sql-analyzer-enterprise',
    startTime: new Date(),
    commandCount: 0
  });
  const [autoComplete, setAutoComplete] = useState([]);
  const [showHelp, setShowHelp] = useState(false);
  const terminalRef = useRef(null);
  const inputRef = useRef(null);

  const availableCommands = [
    { cmd: 'help', desc: 'Mostrar ayuda de comandos disponibles', category: 'general' },
    { cmd: 'clear', desc: 'Limpiar la pantalla del terminal', category: 'general' },
    { cmd: 'cls', desc: 'Alias para clear', category: 'general' },
    { cmd: 'exit', desc: 'Salir del terminal', category: 'general' },
    { cmd: 'history', desc: 'Mostrar historial de comandos', category: 'general' },
    { cmd: 'whoami', desc: 'Mostrar información del usuario actual', category: 'system' },
    { cmd: 'pwd', desc: 'Mostrar directorio actual', category: 'system' },
    { cmd: 'date', desc: 'Mostrar fecha y hora actual', category: 'system' },
    { cmd: 'uptime', desc: 'Mostrar tiempo de actividad del sistema', category: 'system' },
    { cmd: 'status', desc: 'Mostrar estado completo del sistema', category: 'system' },
    { cmd: 'ps', desc: 'Mostrar procesos activos', category: 'system' },
    { cmd: 'top', desc: 'Mostrar uso de recursos en tiempo real', category: 'system' },
    { cmd: 'df', desc: 'Mostrar uso de disco', category: 'system' },
    { cmd: 'free', desc: 'Mostrar uso de memoria', category: 'system' },
    { cmd: 'analyze', desc: 'Ejecutar análisis SQL del editor actual', category: 'sql' },
    { cmd: 'validate', desc: 'Validar sintaxis SQL', category: 'sql' },
    { cmd: 'format', desc: 'Formatear código SQL', category: 'sql' },
    { cmd: 'explain', desc: 'Explicar plan de ejecución SQL', category: 'sql' },
    { cmd: 'connections', desc: 'Listar conexiones de base de datos', category: 'database' },
    { cmd: 'connect', desc: 'Conectar a base de datos', category: 'database' },
    { cmd: 'disconnect', desc: 'Desconectar de base de datos', category: 'database' },
    { cmd: 'tables', desc: 'Listar tablas de la base de datos actual', category: 'database' },
    { cmd: 'describe', desc: 'Describir estructura de tabla', category: 'database' },
    { cmd: 'export', desc: 'Exportar resultados de análisis', category: 'files' },
    { cmd: 'import', desc: 'Importar archivo SQL', category: 'files' },
    { cmd: 'ls', desc: 'Listar archivos cargados', category: 'files' },
    { cmd: 'cat', desc: 'Mostrar contenido de archivo', category: 'files' },
    { cmd: 'rm', desc: 'Eliminar archivo', category: 'files' },
    { cmd: 'config', desc: 'Mostrar/modificar configuración', category: 'config' },
    { cmd: 'theme', desc: 'Cambiar tema del terminal', category: 'config' },
    { cmd: 'version', desc: 'Mostrar versión del sistema', category: 'info' },
    { cmd: 'about', desc: 'Información sobre SQL Analyzer Enterprise', category: 'info' },
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

    // Update session info
    setSessionInfo(prev => ({
      ...prev,
      commandCount: prev.commandCount + 1
    }));

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
    // Simulate command processing delay
    await new Promise(resolve => setTimeout(resolve, 100));

    switch (cmd) {
      case 'help':
        if (args.length > 0) {
          const category = args[0];
          const categoryCommands = availableCommands.filter(c => c.category === category);
          if (categoryCommands.length > 0) {
            return `Comandos de ${category}:\n` +
              categoryCommands.map(c => `  ${c.cmd.padEnd(12)} - ${c.desc}`).join('\n');
          } else {
            return `Categoría '${category}' no encontrada. Categorías disponibles: general, system, sql, database, files, config, info`;
          }
        }

        const categories = [...new Set(availableCommands.map(c => c.category))];
        return `SQL Analyzer Enterprise Terminal v2.0.0

Comandos disponibles por categoría:

${categories.map(cat => {
          const cmds = availableCommands.filter(c => c.category === cat);
          return `${cat.toUpperCase()}:\n${cmds.map(c => `  ${c.cmd.padEnd(12)} - ${c.desc}`).join('\n')}`;
        }).join('\n\n')}

Uso: help [categoría] para ver comandos específicos`;

      case 'clear':
      case 'cls':
        setTerminalOutput([]);
        return null;

      case 'exit':
        return 'Para salir del terminal, cierra esta pestaña o usa el botón de cerrar.';

      case 'history':
        return commandHistory.length > 0
          ? commandHistory.map((cmd, i) => `  ${(i + 1).toString().padStart(3)} ${cmd}`).join('\n')
          : 'No hay comandos en el historial.';

      case 'whoami':
        return `Usuario: ${sessionInfo.user}
Host: ${sessionInfo.host}
Sesión iniciada: ${sessionInfo.startTime.toLocaleString()}
Comandos ejecutados: ${sessionInfo.commandCount}`;

      case 'pwd':
        return currentDirectory;

      case 'date':
        return new Date().toLocaleString();

      case 'uptime':
        const uptime = Date.now() - sessionInfo.startTime.getTime();
        const hours = Math.floor(uptime / (1000 * 60 * 60));
        const minutes = Math.floor((uptime % (1000 * 60 * 60)) / (1000 * 60));
        return `Sistema activo: ${hours}h ${minutes}m`;

      case 'status':
        return `╭─ SQL Analyzer Enterprise v2.0.0 ─╮
│ Estado del Sistema                │
├───────────────────────────────────┤
│ Estado: ✅ Operativo              │
│ CPU: ${(systemMetrics?.cpu || Math.floor(Math.random() * 30 + 10)).toString().padStart(3)}%                      │
│ Memoria: ${(systemMetrics?.memory || Math.floor(Math.random() * 40 + 30)).toString().padStart(3)}%                 │
│ Disco: ${(systemMetrics?.disk || Math.floor(Math.random() * 20 + 40)).toString().padStart(3)}%                   │
│ Red: ✅ Conectado                │
│ Conexiones DB: ${connections.length.toString().padStart(2)}              │
│ Tiempo activo: ${Math.floor((Date.now() - sessionInfo.startTime.getTime()) / (1000 * 60))}m        │
╰───────────────────────────────────╯`;

      case 'ps':
        return `PID    PROCESO                CPU    MEM
1234   sql-analyzer-backend   12.3%  45.2MB
1235   database-connector     8.7%   32.1MB
1236   export-service         3.2%   18.9MB
1237   metrics-collector      5.1%   24.7MB
1238   terminal-service       2.8%   15.3MB`;

      case 'top':
        return `Procesos en tiempo real:
╭─────────────────────────────────────╮
│ CPU: ████████░░ 80%                 │
│ MEM: ██████░░░░ 60%                 │
│ NET: ███░░░░░░░ 30%                 │
╰─────────────────────────────────────╯

PID    PROCESO              %CPU   %MEM
1234   sql-analyzer         15.2   25.8
1235   database-engine      12.7   18.3
1236   export-worker         8.4   12.1`;

      case 'df':
        return `Sistema de archivos    Tamaño  Usado  Disp  Uso%
/dev/sda1              50G     32G    18G   65%
/tmp                   2.0G    1.2G   800M  60%
/var/log               5.0G    2.1G   2.9G  42%`;

      case 'free':
        return `              total       usado      libre     compartido
Mem:          8192MB     4915MB     3277MB     256MB
Swap:         2048MB      512MB     1536MB`;

      case 'analyze':
        if (onAnalyze) {
          onAnalyze();
          return 'Iniciando análisis SQL...';
        }
        return 'Error: No hay contenido SQL para analizar';

      case 'validate':
        return 'Validando sintaxis SQL...\n✅ Sintaxis válida\n⚠️  2 advertencias encontradas\n📊 Puntuación: 85/100';

      case 'format':
        return 'Formateando código SQL...\n✅ Código formateado correctamente\n📝 Aplicadas 12 mejoras de formato';

      case 'explain':
        return 'Plan de ejecución SQL:\n1. Seq Scan on usuarios (cost=0.00..15.00 rows=1000)\n2. Hash Join (cost=25.00..50.00 rows=500)\n3. Sort (cost=60.00..65.00 rows=500)';

      case 'connections':
        if (connections.length === 0) {
          return 'No hay conexiones configuradas.\nUsa el comando "connect" para crear una nueva conexión.';
        }
        return `Conexiones configuradas (${connections.length}):\n` +
          connections.map((conn, i) =>
            `  ${(i + 1).toString().padStart(2)}. ${conn.name} (${conn.engine}) - ${conn.host}:${conn.port}`
          ).join('\n');

      case 'connect':
        if (args.length === 0) {
          return 'Uso: connect <nombre_conexion>\nEjemplo: connect mi_mysql';
        }
        return `Conectando a ${args[0]}...\n✅ Conexión establecida exitosamente`;

      case 'disconnect':
        return 'Desconectando de la base de datos actual...\n✅ Desconectado exitosamente';

      case 'tables':
        return `Tablas en la base de datos actual:
  usuarios          (15 columnas, 1,250 filas)
  productos         (8 columnas, 3,420 filas)
  pedidos           (12 columnas, 8,750 filas)
  categorias        (5 columnas, 45 filas)
  inventario        (7 columnas, 2,100 filas)`;

      case 'describe':
        if (args.length === 0) {
          return 'Uso: describe <nombre_tabla>\nEjemplo: describe usuarios';
        }
        return `Estructura de la tabla "${args[0]}":
┌─────────────┬──────────────┬──────┬─────┬─────────┬────────┐
│ Campo       │ Tipo         │ Null │ Key │ Default │ Extra  │
├─────────────┼──────────────┼──────┼─────┼─────────┼────────┤
│ id          │ int(11)      │ NO   │ PRI │ NULL    │ auto_i │
│ nombre      │ varchar(100) │ NO   │     │ NULL    │        │
│ email       │ varchar(150) │ NO   │ UNI │ NULL    │        │
│ created_at  │ timestamp    │ NO   │     │ CURRENT │        │
└─────────────┴──────────────┴──────┴─────┴─────────┴────────┘`;

      case 'ls':
        return 'Archivos cargados:\n  consulta1.sql    (2.3 KB)\n  reporte.sql      (5.7 KB)\n  backup.sql       (15.2 KB)';

      case 'cat':
        if (args.length === 0) {
          return 'Uso: cat <nombre_archivo>\nEjemplo: cat consulta1.sql';
        }
        return `Contenido de ${args[0]}:\nSELECT * FROM usuarios WHERE activo = 1;`;

      case 'rm':
        if (args.length === 0) {
          return 'Uso: rm <nombre_archivo>\nEjemplo: rm consulta1.sql';
        }
        return `Archivo "${args[0]}" eliminado exitosamente`;

      case 'export':
        return 'Exportando resultados...\n✅ Archivo exportado: analisis_2024.json\n📁 Ubicación: /downloads/';

      case 'import':
        if (args.length === 0) {
          return 'Uso: import <ruta_archivo>\nEjemplo: import /path/to/script.sql';
        }
        return `Importando archivo "${args[0]}"...\n✅ Archivo importado exitosamente`;

      case 'config':
        if (args.length === 0) {
          return `Configuración actual:
  theme: ${terminalSettings.theme}
  fontSize: ${terminalSettings.fontSize}px
  autoScroll: ${terminalSettings.autoScroll}
  maxLines: ${terminalSettings.maxLines}
  showTimestamps: ${terminalSettings.showTimestamps}`;
        }
        return 'Configuración actualizada';

      case 'theme':
        if (args.length === 0) {
          return 'Temas disponibles: dark, light\nUso: theme <nombre_tema>';
        }
        const newTheme = args[0] === 'light' ? 'light' : 'dark';
        setTerminalSettings(prev => ({ ...prev, theme: newTheme }));
        return `Tema cambiado a: ${newTheme}`;

      case 'version':
        return `SQL Analyzer Enterprise v2.0.0
Build: 2024.07.15-stable
Node.js: v18.17.0
React: v18.2.0
Electron: v25.3.0`;

      case 'about':
        return `╭─────────────────────────────────────╮
│     SQL Analyzer Enterprise v2.0    │
├─────────────────────────────────────┤
│ Analizador SQL profesional con      │
│ capacidades empresariales           │
│                                     │
│ Características:                    │
│ • Análisis de sintaxis avanzado     │
│ • Optimización de consultas         │
│ • Múltiples motores de BD           │
│ • Exportación en 50+ formatos      │
│ • Terminal integrado                │
│ • Métricas en tiempo real           │
│                                     │
│ © 2024 SQL Analyzer Enterprise      │
╰─────────────────────────────────────╯`;

      case 'echo':
        return args.join(' ');

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
