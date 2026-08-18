# MCP Agent Platform

A modular Model Context Protocol (MCP) agent platform built with Python.

This project allows an LLM-powered agent to work with both **local tools** and **tools exposed by external MCP servers**. It provides MCP server management, dynamic tool discovery, tool registration, tool execution, and multi-step tool calling.

---

## 🚀 Project Overview

The MCP Agent Platform acts as a bridge between an LLM and multiple tools.

The agent can:

- Register local Python tools
- Connect to external MCP servers
- Discover tools dynamically from MCP servers
- Convert MCP tools into OpenAI-compatible function schemas
- Allow the LLM to decide which tool to use
- Execute the selected tool
- Send tool results back into the LLM context
- Execute multiple tools sequentially when required
- Return the final natural-language response
- Manage MCP server connections through REST APIs
- Expose an MCP server over Streamable HTTP

---

## 🏗️ Architecture

```text
                         ┌──────────────────────┐
                         │        User          │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      Agent / LLM     │
                         │    OpenAI API        │
                         └──────────┬───────────┘
                                    │
                         Tool selection
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    Tool Registry     │
                         └──────────┬───────────┘
                                    │
                  ┌─────────────────┴─────────────────┐
                  │                                   │
                  ▼                                   ▼
        ┌───────────────────┐              ┌───────────────────┐
        │   Local Tools     │              │    MCP Tools      │
        │                   │              │                   │
        │ get_weather       │              │ External MCP      │
        │ get_datetime      │              │ Servers            │
        └─────────┬─────────┘              └─────────┬─────────┘
                  │                                   │
                  │                                   ▼
                  │                         ┌──────────────────┐
                  │                         │   MCP Manager    │
                  │                         └────────┬─────────┘
                  │                                  │
                  │                                  ▼
                  │                         ┌──────────────────┐
                  │                         │  MCP Server(s)   │
                  │                         │ Streamable HTTP  │
                  │                         └────────┬─────────┘
                  │                                  │
                  └──────────────────┬───────────────┘
                                     │
                                     ▼
                              Tool Result
                                     │
                                     ▼
                                  LLM
                                     │
                                     ▼
                              Final Response