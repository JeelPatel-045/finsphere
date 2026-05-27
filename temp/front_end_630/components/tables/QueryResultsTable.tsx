"use client";

import { useEffect, useState } from "react";

import API from "@/lib/api";

export default function QueryResultsTable() {
  const [rows, setRows] = useState([]);

  useEffect(() => {
    loadRows();
  }, []);

  const loadRows = async () => {
    const response =
      await API.get("/sql-agent/results");

    setRows(response.data);
  };

  return (
    <table className="w-full">
      <tbody>
        {rows.map((row: any, index) => (
          <tr key={index}>
            <td>{row.account}</td>
            <td>{row.amount}</td>
            <td>{row.risk}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}