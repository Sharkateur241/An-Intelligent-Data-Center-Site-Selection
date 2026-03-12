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
  ExclamationCircleOutlined,
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
            暂无决策分析数据
          </Title>
          <Text type="secondary">请先进行位置分析</Text>
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
    if (score >= 90) return "优秀";
    if (score >= 75) return "良好";
    if (score >= 60) return "一般";
    if (score >= 45) return "较差";
    return "很差";
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

  // 准备雷达图数据
  const radarData = decision_recommendation?.detailed_scores
    ? Object.entries(decision_recommendation.detailed_scores).map(
        ([criterion, score]: [string, any]) => ({
          criterion: criterion.replace("_", " "),
          score: score.score,
          fullMark: 100,
        })
      )
    : [];

  const criteriaLabels = {
    "land suitability": "土地适宜性",
    "energy resources": "能源资源",
    "grid capacity": "电网容量",
    "economic feasibility": "经济可行性",
    "environmental impact": "环境影响",
  };

  const radarDataWithLabels = radarData.map((item) => ({
    ...item,
    criterion:
      criteriaLabels[item.criterion as keyof typeof criteriaLabels] ||
      item.criterion,
  }));

  return (
    <div>
      <Title level={2}>智能决策分析</Title>

      {/* 综合决策结果 */}
      <Card title="综合决策结果" style={{ marginBottom: 16 }}>
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
              <Title level={3}>决策等级</Title>
              <Tag
                color={getDecisionLevelColor(
                  decision_recommendation?.decision_level || ""
                )}
                style={{ fontSize: "18px", padding: "8px 16px" }}
              >
                {decision_recommendation?.decision_level || "未知"}
              </Tag>
            </div>
          </Col>
          <Col span={8}>
            <div style={{ textAlign: "center" }}>
              <Title level={3}>分析时间</Title>
              <Text type="secondary">
                {new Date(
                  decision_recommendation?.analysis_date || ""
                ).toLocaleString("zh-CN")}
              </Text>
            </div>
          </Col>
        </Row>
      </Card>

      {/* 详细评分雷达图 */}
      <Card title="详细评分分析" style={{ marginBottom: 16 }}>
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
                  name="评分"
                  dataKey="score"
                  stroke="#1890ff"
                  fill="#1890ff"
                  fillOpacity={0.3}
                />
              </RadarChart>
            </ResponsiveContainer>
          </Col>
          <Col span={12}>
            <Title level={4}>各维度评分详情</Title>
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
                    {item.score} 分
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

      {/* 决策建议 */}
      <Card title="决策建议" style={{ marginBottom: 16 }}>
        <List
          dataSource={decision_recommendation?.recommendations || []}
          renderItem={(item: string, index: number) => (
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

      {/* 风险评估 */}
      <Card title="风险评估" style={{ marginBottom: 16 }}>
        <Row gutter={16}>
          <Col span={12}>
            <Title level={4}>风险等级</Title>
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
                {decision_recommendation?.risk_assessment?.risk_level || "未知"}
              </Tag>
            </div>

            {decision_recommendation?.risk_assessment?.risks?.length > 0 && (
              <div>
                <Title level={5}>主要风险</Title>
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
            <Title level={4}>风险缓解措施</Title>
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
                message="暂无风险缓解措施"
                description="当前风险评估显示风险较低，无需特殊缓解措施。"
                type="info"
                showIcon
              />
            )}
          </Col>
        </Row>
      </Card>

      {/* 关键指标统计 */}
      <Card title="关键指标统计">
        <Row gutter={16}>
          <Col span={6}>
            <Statistic
              title="土地适宜性"
              value={
                decision_recommendation?.detailed_scores?.land_suitability
                  ?.score || 0
              }
              suffix="分"
              prefix={<EnvironmentOutlined style={{ color: "#52c41a" }} />}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="能源资源"
              value={
                decision_recommendation?.detailed_scores?.energy_resources
                  ?.score || 0
              }
              suffix="分"
              prefix={<ThunderboltOutlined style={{ color: "#faad14" }} />}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="经济可行性"
              value={
                decision_recommendation?.detailed_scores?.economic_feasibility
                  ?.score || 0
              }
              suffix="分"
              prefix={<DollarOutlined style={{ color: "#1890ff" }} />}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="环境影响"
              value={
                decision_recommendation?.detailed_scores?.environmental_impact
                  ?.score || 0
              }
              suffix="分"
              prefix={<SafetyOutlined style={{ color: "#52c41a" }} />}
            />
          </Col>
        </Row>
      </Card>
    </div>
  );
};

export default DecisionAnalysis;
