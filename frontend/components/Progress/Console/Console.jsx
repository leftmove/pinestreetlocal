import styles from "../Progress.module.css";
import { useEffect, useRef } from "react";

import { Inter } from "@next/font/google";
const interLight = Inter({ subsets: ["latin"], weight: "700" });

import useEllipsis from "@/components/Hooks/useEllipsis";

const Console = (props) => {
  const logs = props.logs;
  const stall = props.stall || true;

  const { ellipsis } = useEllipsis();
  const ref = useRef(null);
  useEffect(() => {
    ref.current.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [logs]);

  return (
    <div className={styles["logs"]}>
      {logs.map((log, index) => {
        return (
          <span
            key={index}
            className={[styles["log"], interLight.className].join(" ")}
          >
            {log}
          </span>
        );
      })}
      <span className={[styles["log"], interLight.className].join(" ")}>
        {stall ? null : ellipsis}
      </span>
      <div className={styles["bottom"]} ref={ref}></div>
    </div>
  );
};

export default Console;