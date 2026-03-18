import React from 'react';
import { Card, Row, Col, Typography, Progress, Tag, List, Divider } from 'antd';
import { 
  EnvironmentOutlined, 
  ThunderboltOutlined, 
  BulbOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons';

const { Title, Text } = Typography;

interface AnalysisResultsProps {
  data: any;
}

const translateLevel = (val?: string) => {
  if (val === '高') return 'High';
  if (val === '中') return 'Medium';
  if (val === '低') return 'Low';
  return val || '';
};

const AnalysisResults: React.FC<AnalysisResultsProps> = ({ data }) => {
  if (!data) {
    return (
      <Card>
        <div style={{ textAlign: 'center', padding: '50px' }}>
          <ExclamationCircleOutlined style={{ fontSize: '48px', color: '#ccc' }} />
          <Title level={4} style={{ color: '#ccc', marginTop: '16px' }}>
            No analysis data
          </Title>
          <Text type="secondary">Select a location on the map and run analysis</Text>
        </div>
      </Card>
    );
  }

  const { land_analysis, energy_assessment, decision_recommendation, heat_utilization } = data;

  const getScoreColor = (score: number) => {
    if (score >= 90) return '#52c41a';
    if (score >= 75) return '#1890ff';
    if (score >= 60) return '#faad14';
    if (score >= 45) return '#ff7875';
    return '#f5222d';
  };

  const getScoreLevel = (score: number) => {
    if (score >= 90) return 'Excellent';
    if (score >= 75) return 'Good';
    if (score >= 60) return 'Fair';
    if (score >= 45) return 'Poor';
    return 'Very poor';
  };

  return (
    <div>
      <Title level={2}>Analysis Overview</Title>
      
      {/* Land use analysis */}
      <Card title="Land Use Analysis" style={{ marginBottom: 16 }}>
        <Row gutter={16}>
          <Col span={12}>
            <Title level={4}>Land Cover Distribution</Title>
            {land_analysis?.land_use_distribution && Object.entries(land_analysis.land_use_distribution).map(([type, ratio]: [string, any]) => (
              <div key={type} style={{ marginBottom: 8 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                  <Text>{type}</Text>
                  <Text strong>{(ratio * 100).toFixed(1)}%</Text>
                </div>
                <Progress 
                  percent={ratio * 100} 
                  size="small" 
                  strokeColor={getScoreColor(ratio * 100)}
                />
              </div>
            ))}
          </Col>
          <Col span={12}>
            <Title level={4}>Suitable Areas</Title>
            {land_analysis?.suitable_areas?.map((area: any, index: number) => (
              <Card key={index} size="small" style={{ marginBottom: 8 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Text strong>{area.type}</Text>
                  <Tag color={getScoreColor(area.suitability_score * 100)}>
                    {getScoreLevel(area.suitability_score * 100)}
                  </Tag>
                </div>
                <Text type="secondary">Area share: {(area.area_ratio * 100).toFixed(1)}%</Text>
              </Card>
            ))}
          </Col>
        </Row>
        
        {land_analysis?.recommendations && (
          <div style={{ marginTop: 16 }}>
            <Title level={4}>Land Use Recommendations</Title>
            <List
              dataSource={land_analysis.recommendations}
              renderItem={(item: string) => (
                <List.Item>
                  <CheckCircleOutlined style={{ color: '#52c41a', marginRight: 8 }} />
                  {item}
                </List.Item>
              )}
            />
          </div>
        )}
      </Card>

      {/* Energy assessment */}
      <Card title="Energy Resources Assessment" style={{ marginBottom: 16 }}>
        <Row gutter={16}>
          <Col span={8}>
            <Card size="small">
              <div style={{ textAlign: 'center' }}>
                <ThunderboltOutlined style={{ fontSize: '24px', color: '#faad14' }} />
                <Title level={4}>Solar Resource</Title>
                <Text strong>{energy_assessment?.solar_data?.solar_zone}</Text><br />
                <Text>Annual irradiance: {energy_assessment?.solar_data?.annual_irradiance} kWh/m²</Text><br />
                <Tag color={energy_assessment?.solar_data?.solar_potential === '高' ? 'green' : 'orange'}>
                  {translateLevel(energy_assessment?.solar_data?.solar_potential)}
                </Tag>
              </div>
            </Card>
          </Col>
          <Col span={8}>
            <Card size="small">
              <div style={{ textAlign: 'center' }}>
                <EnvironmentOutlined style={{ fontSize: '24px', color: '#1890ff' }} />
                <Title level={4}>Wind Resource</Title>
                <Text strong>{energy_assessment?.wind_data?.wind_zone}</Text><br />
                <Text>Average wind speed: {energy_assessment?.wind_data?.average_speed} m/s</Text><br />
                <Tag color={energy_assessment?.wind_data?.wind_potential === '高' ? 'green' : 'orange'}>
                  {translateLevel(energy_assessment?.wind_data?.wind_potential)}
                </Tag>
              </div>
            </Card>
          </Col>
          <Col span={8}>
            <Card size="small">
              <div style={{ textAlign: 'center' }}>
                <BulbOutlined style={{ fontSize: '24px', color: '#52c41a' }} />
                <Title level={4}>Renewable Potential</Title>
                <Text strong>
                  {energy_assessment?.renewable_potential?.total_renewable_potential?.annual_generation_mwh?.toFixed(0)} MWh/yr
                </Text><br />
                <Text>Coverage: {(energy_assessment?.storage_assessment?.renewable_coverage * 100).toFixed(1)}%</Text>
              </div>
            </Card>
          </Col>
        </Row>
      </Card>

      {/* Decision analysis */}
      <Card title="Decision Analysis" style={{ marginBottom: 16 }}>
        <Row gutter={16}>
          <Col span={12}>
            <Title level={4}>Overall Score</Title>
            <div style={{ textAlign: 'center', marginBottom: 16 }}>
              <Progress
                type="circle"
                percent={decision_recommendation?.overall_score?.score || 0}
                strokeColor={getScoreColor(decision_recommendation?.overall_score?.score || 0)}
                format={(percent) => (
                  <div>
                    <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{percent}</div>
                    <div style={{ fontSize: '12px' }}>
                      {getScoreLevel(decision_recommendation?.overall_score?.score || 0)}
                    </div>
                  </div>
                )}
              />
            </div>
          </Col>
          <Col span={12}>
            <Title level={4}>Detailed Scores</Title>
            {decision_recommendation?.detailed_scores && Object.entries(decision_recommendation.detailed_scores).map(([criterion, score]: [string, any]) => (
              <div key={criterion} style={{ marginBottom: 8 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                  <Text>{criterion}</Text>
                  <Text strong>{score.score}</Text>
                </div>
                <Progress 
                  percent={score.score} 
                  size="small" 
                  strokeColor={getScoreColor(score.score)}
                />
              </div>
            ))}
          </Col>
        </Row>
        
        <Divider />
        
        <Title level={4}>Decision Recommendations</Title>
        <List
          dataSource={decision_recommendation?.recommendations || []}
          renderItem={(item: string) => (
            <List.Item>
              <CheckCircleOutlined style={{ color: '#52c41a', marginRight: 8 }} />
              {item}
            </List.Item>
          )}
        />
      </Card>

      {/* Waste heat utilization */}
      <Card title="Waste Heat Utilization">
        <Row gutter={16}>
          <Col span={12}>
            <Title level={4}>Recoverable Heat</Title>
            <Text strong style={{ fontSize: '18px', color: '#1890ff' }}>
              {heat_utilization?.recoverable_heat_mw} MW
            </Text>
            <div style={{ marginTop: 16 }}>
              <Title level={5}>Utilization Schemes</Title>
              {heat_utilization?.utilization_options?.map((option: any, index: number) => (
                <Card key={index} size="small" style={{ marginBottom: 8 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Text strong>{option.type}</Text>
                    <Tag color={option.feasibility === '高' ? 'green' : 'orange'}>
                      {translateLevel(option.feasibility)}
                    </Tag>
                  </div>
                  <Text type="secondary">Capacity: {option.capacity_mw} MW</Text><br />
                  <Text type="secondary">Target users: {option.target_users}</Text><br />
                  <Text type="secondary">Annual revenue: {option.economic_value.toLocaleString()} RMB</Text>
                </Card>
              ))}
            </div>
          </Col>
          <Col span={12}>
            <Title level={4}>Economic Benefits</Title>
            <div style={{ textAlign: 'center', marginBottom: 16 }}>
              <Text strong style={{ fontSize: '24px', color: '#52c41a' }}>
                {heat_utilization?.economic_benefits?.annual_revenue?.toLocaleString()} RMB/yr
              </Text>
              <div style={{ marginTop: 8 }}>
                <Text>Payback period: {heat_utilization?.economic_benefits?.payback_period} yrs</Text><br />
                <Text>CO₂ reduction: {heat_utilization?.economic_benefits?.co2_reduction?.toFixed(0)} tons/yr</Text>
              </div>
            </div>
            
            <Title level={5}>Waste Heat Recommendations</Title>
            <List
              dataSource={heat_utilization?.recommendations || []}
              renderItem={(item: string) => (
                <List.Item>
                  <CheckCircleOutlined style={{ color: '#52c41a', marginRight: 8 }} />
                  {item}
                </List.Item>
              )}
            />
          </Col>
        </Row>
      </Card>
    </div>
  );
};

export default AnalysisResults;
