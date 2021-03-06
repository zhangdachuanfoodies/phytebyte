import pytest
from unittest.mock import Mock, MagicMock

from phytebyte.bioactive_cmpd.model_input_loader import ModelInputLoader


@pytest.fixture
def output_fingerprinter():
    return Mock()


@pytest.fixture
def mock_source():
    m = Mock()
    return m


@pytest.fixture
def mock_negative_sampler():
    m = Mock()
    return m


@pytest.fixture
def mock_encoded_cmpds():
    return [Mock(), Mock()]


@pytest.fixture
def mock_clusters(mock_encoded_cmpds):
    cluster1 = Mock()
    cluster2 = Mock()
    cluster1.get_encoded_cmpds = MagicMock(return_value=mock_encoded_cmpds)
    cluster2.get_encoded_cmpds = MagicMock(return_value=mock_encoded_cmpds)
    return [cluster1, cluster2]


@pytest.fixture
def mock_positive_clusterer(mock_clusters):
    m = Mock()
    m.find_clusters = MagicMock(return_value=mock_clusters)
    return m


@pytest.fixture
def mock_target_input():
    m = Mock()
    m.fetch_bioactive_cmpds = MagicMock(
        return_value=[lambda: Mock()])
    return m


@pytest.fixture
def mock_encoding():
    return "numpy"


@pytest.fixture
def mock_binary_classifier_input():
    return Mock()


@pytest.fixture
def model_input_loader(mock_source, mock_negative_sampler,
                       mock_positive_clusterer, mock_target_input,
                       mock_encoding, mock_binary_classifier_input):
    mil = ModelInputLoader(mock_source, mock_negative_sampler,
                           mock_positive_clusterer, mock_target_input, 'numpy')
    mil._get_neg_bioactive_cmpd_iters = MagicMock(
        return_value=[iter(['C=O', 'C=N']), iter(['C', 'H2O'])])
    mil._create_binary_classifier_input = MagicMock(
        return_value=mock_binary_classifier_input)
    return mil


def test_init(mock_source, mock_negative_sampler,
              mock_positive_clusterer, mock_target_input, mock_encoding):
    mil = ModelInputLoader(mock_source, mock_negative_sampler,
                           mock_positive_clusterer, mock_target_input, 'numpy')
    assert mil is not None


def test_load(model_input_loader, mock_binary_classifier_input):
    model_inputs = model_input_loader.load(2, output_fingerprinter)
    assert model_inputs == [
        mock_binary_classifier_input] * 2


def test_load__calls_BinaryClassifierInputFactory_create(
        mock_binary_classifier_input, monkeypatch,
        mock_source, mock_negative_sampler, mock_positive_clusterer,
        mock_target_input, mock_encoding):
    mil = ModelInputLoader(mock_source, mock_negative_sampler,
                           mock_positive_clusterer, mock_target_input, 'numpy')
    mil._get_neg_bioactive_cmpd_iters = MagicMock(
        return_value=[iter(['C=O', 'C=N']), iter(['C', 'H2O'])])
    mock_bcif = Mock()
    mock_bcif.create = MagicMock(return_value=Mock())
    monkeypatch.setattr("phytebyte.bioactive_cmpd.model_input_loader."
                        "BinaryClassifierInputFactory", mock_bcif)
    mil.load(2, output_fingerprinter)
    call_args_ls = mock_bcif.create.call_args_list
    assert len(call_args_ls) == 2
    assert set(call_args_ls[0][1].keys()) == set(
        ['encoding', 'positives', 'negatives'])
    assert set(call_args_ls[1][1].keys()) == set(
        ['encoding', 'positives', 'negatives'])


def test_load__calls_get_encoded_cmpds(mock_source,
                                       mock_negative_sampler,
                                       mock_positive_clusterer,
                                       mock_target_input,
                                       mock_clusters,
                                       mock_encoding,
                                       monkeypatch):
    mil = ModelInputLoader(mock_source, mock_negative_sampler,
                           mock_positive_clusterer, mock_target_input, 'numpy')
    mil._get_neg_bioactive_cmpd_iters = MagicMock(
        return_value=[iter(['C=O', 'C=N']), iter(['C', 'H2O'])])
    mock_bcif = Mock()
    mock_bcif.create = MagicMock(return_value=Mock())
    monkeypatch.setattr("phytebyte.bioactive_cmpd.model_input_loader."
                        "BinaryClassifierInputFactory", mock_bcif)
    mil.load(2, output_fingerprinter)

    mock_clusters[0].get_encoded_cmpds.assert_called_once()
    mock_clusters[1].get_encoded_cmpds.assert_called_once()
