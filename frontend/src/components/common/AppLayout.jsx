import { useEffect, useState } from "react";
import { useLocation, useOutlet } from "react-router-dom";
import Navbar from "./Navbar";
import Sidebar from "./Sidebar";

export default function AppLayout() {
  const location = useLocation();
  const currentOutlet = useOutlet();

  const [stage, setStage] = useState({
    currentKey: location.pathname,
    currentNode: currentOutlet,
    exitingKey: null,
    exitingNode: null,
  });

  if (stage.currentKey !== location.pathname) {
    setStage({
      currentKey: location.pathname,
      currentNode: currentOutlet,
      exitingKey: stage.currentKey,
      exitingNode: stage.currentNode,
    });
  }

  useEffect(() => {
    if (!stage.exitingKey) return undefined;
    const timer = setTimeout(() => {
      setStage((prev) => ({
        ...prev,
        exitingKey: null,
        exitingNode: null,
      }));
    }, 300);
    return () => clearTimeout(timer);
  }, [stage.exitingKey]);

  return (
    <div className="app-shell">
      <Navbar />
      <div className="app-body">
        <Sidebar />
        <main className="main-content">
          <div className="tab-transition-stage">
            {stage.exitingNode && (
              <div
                key={`exit-${stage.exitingKey}`}
                className="tab-page-pane tab-page-exit"
                aria-hidden="true"
              >
                {stage.exitingNode}
              </div>
            )}
            <div
              key={stage.currentKey}
              className={
                stage.exitingNode
                  ? "tab-page-pane tab-page-enter"
                  : "tab-page-pane tab-page-initial"
              }
            >
              {currentOutlet}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
