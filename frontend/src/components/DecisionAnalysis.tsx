import React from "react";
import {
  Card,
  Row,
  Col,
  Typography,
  Progress,
  Tag,
  List,
  Alert,
  Statistic,
} from "antd";
import {
  CheckCircleOutlined,
  WarningOutlined,
  BulbOutlined,
  ThunderboltOutlined,
  EnvironmentOutlined,
  DollarOutlined,
  SafetyOutlined,
} from "@ant-design/icons";
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
} from "recharts";

const { Title, Text } = Typography;

interface DecisionAnalysisProps {
  data: any;
}

const DecisionAnalysis: React.FC<DecisionAnalysisProps> = ({ data }) => {
  if (!data) {
    return (
      <Card>
        <div style={{ textAlign: "center", padding: "50px" }}>
          <BulbOutlined style={{ fontSize: "48px", color: "#ccc" }} />
          <Title level={4} style={{ color: "#ccc", marginTop: "16px" }}>
            No decision analysis data
          </Title>
          <Text type="secondary">Run a location analysis first</Text>
        </div>
      </Card>
    );
  }

  const { decision_recommendation } = data;

  const getScoreColor = (score: number) => {
    if (score >= 90) return "#52c41a";
    if (score >= 75) return "#1890ff";
    if (score >= 60) return "#faad14";
    if (score >= 45) return "#ff7875";
    return "#f5222d";
  };

  const getScoreLevel = (score: number) => {
    if (score >= 90) return "Excellent";
    if (score >= 75) return "Good";
    if (score >= 60) return "Fair";
    if (score >= 45) return "Poor";
    return "Very poor";
  };

  const getDecisionLevelColor = (level: string) => {
    switch (level) {
      case "强烈推荐":
        return "green";
      case "推荐":
        return "blue";
      case "可以考虑":
        return "orange";
      case "不推荐":
        return "red";
      case "强烈不推荐":
        return "red";
      default:
        return "default";
    }
  };
  const translateDecisionLevel = (level: string) => {
    switch (level) {
      case "强烈推荐":
        return "Strongly Recommended";
      case "推荐":
        return "Recommended";
      case "可以考虑":
        return "Consider with Caution";
      case "不推荐":
        return "Not Recommended";
      case "强烈不推荐":
        return "Strongly Not Recommended";
      default:
        return level || "Unknown";
    }
  };
  const translateRisk = (level?: string) => {
    if (level === "低") return "Low";
    if (level === "中") return "Medium";
    if (level === "高") return "High";
    return level || "Unknown";
  };

  // Prepare radar chart data
  const radarData = decision_recommendation?.detailed_scores
    ? Object.entries(decision_recommendation.detailed_scores).map(
        ([criterion, score]: [string, any]) => ({
          criterion: criterion.replace(/_/g, " "),
          score: score?.score ?? 0,
          fullMark: 100,
        })
      )
    : [];

  const criteriaLabels = {
    "land suitability": "Land suitability",
    "energy resources": "Energy resources",
    "grid capacity": "Grid capacity",
    "economic feasibility": "Economic feasibility",
    "environmental impact": "Environmental impact",
  };

  const radarDataWithLabels = radarData.map((item) => ({
    ...item,
    criterion:
      criteriaLabels[item.criterion as keyof typeof criteriaLabels] ||
      item.criterion,
  }));

  return (
    <div>
      <Title level={2}>AI Decision Analysis</Title>

      {/* Overall decision result */}
      <Card title="Overall Decision Result" style={{ marginBottom: 16 }}>
        <Row gutter={16} align="middle">
          <Col span={8}>
            <div style={{ textAlign: "center" }}>
              <Progress
                type="circle"
                percent={decision_recommendation?.overall_score?.score || 0}
                strokeColor={getScoreColor(
                  decision_recommendation?.overall_score?.score || 0
                )}
                format={(percent) => (
                  <div>
                    <div style={{ fontSize: "32px", fontWeight: "bold" }}>
                      {percent}
                    </div>
                    <div style={{ fontSize: "14px" }}>
                      {getScoreLevel(
                        decision_recommendation?.overall_score?.score || 0
                      )}
                    </div>
                  </div>
                )}
              />
            </div>
          </Col>
          <Col span={8}>
            <div style={{ textAlign: "center" }}>
              <Title level={3}>Decision Level</Title>
              <Tag
                color={getDecisionLevelColor(
                  decision_recommendation?.decision_level || ""
                )}
                style={{ fontSize: "18px", padding: "8px 16px" }}
              >
                {translateDecisionLevel(decision_recommendation?.decision_level || "")}
              </Tag>
            </div>
          </Col>
          <Col span={8}>
            <div style={{ textAlign: "center" }}>
              <Title level={3}>Analysis Time</Title>
              <Text type="secondary">
                {(() => {
                  const d = new Date(decision_recommendation?.analysis_date || "");
                  return isNaN(d.getTime()) ? "N/A" : d.toLocaleString();
                })()}
              </Text>
            </div>
          </Col>
        </Row>
      </Card>

      {/* Detailed scores radar */}
      <Card title="Detailed Scores" style={{ marginBottom: 16 }}>
        <Row gutter={16}>
          <Col span={12}>
            <ResponsiveContainer width="100%" height={400}>
              <RadarChart data={radarDataWithLabels}>
                <PolarGrid />
                <PolarAngleAxis
                  dataKey="criterion"
                  tick={{ fill: "#14b8a6" }}
                />
                <PolarRadiusAxis angle={90} domain={[0, 100]} />
                <Radar
                  name="Score"
                  dataKey="score"
                  stroke="#1890ff"
                  fill="#1890ff"
                  fillOpacity={0.3}
                />
              </RadarChart>
            </ResponsiveContainer>
          </Col>
          <Col span={12}>
            <Title level={4}>Dimension Score Details</Title>
            {radarDataWithLabels.map((item, index) => (
              <div key={index} style={{ marginBottom: 16 }}>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    marginBottom: 8,
                  }}
                >
                  <Text strong>{item.criterion}</Text>
                  <Text strong style={{ color: getScoreColor(item.score) }}>
                    {item.score} pts
                  </Text>
                </div>
                <Progress
                  percent={item.score}
                  strokeColor={getScoreColor(item.score)}
                  format={() => getScoreLevel(item.score)}
                />
              </div>
            ))}
          </Col>
        </Row>
      </Card>

      {/* Decision recommendations */}
      <Card title="Decision Recommendations" style={{ marginBottom: 16 }}>
        <List
          dataSource={decision_recommendation?.recommendations || []}
          renderItem={(item: string) => (
            <List.Item>
              <div
                style={{
                  display: "flex",
                  alignItems: "flex-start",
                  width: "100%",
                }}
              >
                <CheckCircleOutlined
                  style={{
                    color: "#52c41a",
                    marginRight: 12,
                    marginTop: 2,
                    fontSize: "16px",
                  }}
                />
                <div style={{ flex: 1 }}>
                  <Text>{item}</Text>
                </div>
              </div>
            </List.Item>
          )}
        />
      </Card>

      {/* Risk assessment */}
      <Card title="Risk Assessment" style={{ marginBottom: 16 }}>
        <Row gutter={16}>
          <Col span={12}>
            <Title level={4}>Risk Level</Title>
            <div style={{ textAlign: "center", marginBottom: 16 }}>
              <Tag
                color={
                  decision_recommendation?.risk_assessment?.risk_level === "低"
                    ? "green"
                    : decision_recommendation?.risk_assessment?.risk_level ===
                      "中"
                    ? "orange"
                    : "red"
                }
                style={{ fontSize: "18px", padding: "8px 16px" }}
              >
                {translateRisk(decision_recommendation?.risk_assessment?.risk_level)}
              </Tag>
            </div>

            {decision_recommendation?.risk_assessment?.risks?.length > 0 && (
              <div>
                <Title level={5}>Key Risks</Title>
                <List
                  dataSource={decision_recommendation.risk_assessment.risks}
                  renderItem={(risk: string) => (
                    <List.Item>
                      <WarningOutlined
                        style={{ color: "#faad14", marginRight: 8 }}
                      />
                      <Text>{risk}</Text>
                    </List.Item>
                  )}
                />
              </div>
            )}
          </Col>
          <Col span={12}>
            <Title level={4}>Mitigations</Title>
            {decision_recommendation?.risk_assessment?.mitigation_measures
              ?.length > 0 ? (
              <List
                dataSource={
                  decision_recommendation.risk_assessment.mitigation_measures
                }
                renderItem={(measure: string) => (
                  <List.Item>
                    <SafetyOutlined
                      style={{ color: "#1890ff", marginRight: 8 }}
                    />
                    <Text>{measure}</Text>
                  </List.Item>
                )}
              />
            ) : (
              <Alert
                message="No mitigation actions provided"
                description="Current assessment shows low risk; no special mitigation required."
                type="info"
                showIcon
              />
            )}
          </Col>
        </Row>
      </Card>

      {/* Key metrics */}
      <Card title="Key Metrics">
        <Row gutter={16}>
          <Col span={6}>
            <Statistic
              title="Land suitability"
              value={
                decision_recommendation?.detailed_scores?.land_suitability
                  ?.score || 0
              }
              suffix="pts"
              prefix={<EnvironmentOutlined style={{ color: "#52c41a" }} />}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="Energy resources"
              value={
                decision_recommendation?.detailed_scores?.energy_resources
                  ?.score || 0
              }
              suffix="pts"
              prefix={<ThunderboltOutlined style={{ color: "#faad14" }} />}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="Economic feasibility"
              value={
                decision_recommendation?.detailed_scores?.economic_feasibility
                  ?.score || 0
              }
              suffix="pts"
              prefix={<DollarOutlined style={{ color: "#1890ff" }} />}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="Environmental impact"
              value={
                decision_recommendation?.detailed_scores?.environmental_impact
                  ?.score || 0
              }
              suffix="pts"
              prefix={<SafetyOutlined style={{ color: "#52c41a" }} />}
            />
          </Col>
        </Row>
      </Card>
    </div>
  );
};

export default DecisionAnalysis;
