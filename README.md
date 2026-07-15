<div>
    <h1>Microsoft Azure AI Agent Open Hack</h1>
</div>

**Table of Content**

- [Description](#description)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Set up Environment](#set-up-environment)

## Description

This repository contains the learning materials and code for the **Microsoft Azure AI Agent Open Hack**.

The Open Hack is a collaborative, hands-on developer challenge designed to guide participants through the practical process of building, testing, and deploying AI agents to solve real-world business scenarios. Using [Microsoft Foundry](https://ai.azure.com/home), [VS Code](https://code.visualstudio.com/), and the agentic capabilities of [GitHub Copilot](https://github.com/features/copilot), the resources here help you learn how to create intelligent systems that increase operational efficiency while staying within a streamlined developer workflow.

This [Open Hack Challenge](https://mango-stone-09ac1f10f.7.azurestaticapps.net/) aims at building an AI-powered pizza-ordering agent using Microsoft Foundry. The journey begins with setting up the development environment and deploying a model, followed by creating a basic agent and configuring instructions and persistent memory to keep conversations on-topic. As the challenge advances, participants integrate Contoso Pizza store data, implement a function to estimate pizza quantities based on group size, and finally connect the agent to a Model Context Protocol (MCP) server, enabling it to successfully place, track, and cancel real orders.

## Getting Started

### Prerequisites

- Git
- [Python >= 3.12](https://www.python.org/downloads/)
- [Poetry >= 2](https://python-poetry.org/)
- [Microsoft Azure Account](https://azure.microsoft.com/en-us/free/)
- [Microsoft Azure CLI](https://learn.microsoft.com/en-us/cli/azure/get-started-with-azure-cli?view=azure-cli-latest#install-or-run-in-azure-cloud-shell)

### Set up Environment

- Clone project from GitHub

  ```plaintext
  git clone https://github.com/qhreul/ms-ai-agent-open-hack.git
  cd ms-ai-agent-open-hack
  ```

- Configure access to Poetry virtual environment

  ```plaintext
  poetry config virtualenvs.in-project true
  ```

- Install dependencies

  ```plaintext
  poetry install
  ```
